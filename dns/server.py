import socket
import time
from dnslib import DNSRecord, DNSHeader, QTYPE, RCODE
from dns.cache import DNSCache
from dns.policy import PolicyEngine
from dns.logger import DNSLogger

UPSTREAM_DNS = ("8.8.8.8", 53)
LISTEN_ADDR = ("0.0.0.0", 5300)

policy_engine = PolicyEngine()
logger = DNSLogger()

cache = DNSCache()


def extract_ttl(dns_response):
    if not dns_response.rr:
        return 0
    return min(rr.ttl for rr in dns_response.rr)


def run_dns_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(None)  # Keep blocking behavior but handle errors
    sock.bind(LISTEN_ADDR)

    print(f"[+] DNS Proxy listening on {LISTEN_ADDR[0]}:{LISTEN_ADDR[1]}")

    while True:
        data, client_addr = sock.recvfrom(4096)
        start = time.time()
        now = time.time()

        try:
            request = DNSRecord.parse(data)
            qname = str(request.q.qname).lower()
            qtype = QTYPE[request.q.qtype]
            cache_key = (qname, qtype)

            # print(f"[QUERY] {client_addr[0]} → {qname} ({qtype})")

            base_event = {
                "client_ip": client_addr[0],
                "domain": qname,
                "qtype": qtype
            }

            
            allowed, category = policy_engine.is_allowed(
                client_addr[0],
                qname
            )

            if not allowed:
                reply = DNSRecord(
                    DNSHeader(id=request.header.id, qr=1, aa=1, ra=1, rcode=RCODE.NXDOMAIN),
                    q = request.q
                )
                sock.sendto(reply.pack(), client_addr)
                # print(
                #     f"[POLICY BLOCK] client={client_addr[0]} "
                #     f"domain={qname} category={category}"
                # )
                logger.log({
                    **base_event,
                    "category": category,
                    "decision": "BLOCK",
                    "reason": "policy_denied",
                    "cache":"NA",
                    "latency_ms": 0
                })
                continue

            # CACHE LOOKUP
            cached = cache.get(cache_key, now)
            if cached:
                cached.header.id = request.header.id
                sock.sendto(cached.pack(), client_addr)
                latency = (time.time() - start) * 1000
                # print(
                #     f"[CACHE HIT] {qname} | {latency:.2f} ms "
                #     f"(hits={cache.hits}, misses={cache.misses})"
                # )
                logger.log({
                    **base_event,
                    "category": category,
                    "decision":"ALLOW",
                    "cache":"HIT",
                    "latency_ms":round(
                        (time.time()-start)*1000, 2
                    )
                })
                continue

            # CACHE MISS
            cache.misses += 1

            # UPSTREAM QUERY
            upstream = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            upstream.settimeout(5.0)  # Add timeout
            upstream.sendto(data, UPSTREAM_DNS)
            response_data, _ = upstream.recvfrom(4096)
            upstream.close()  # Close the socket

            response = DNSRecord.parse(response_data)
            ttl = extract_ttl(response)

            cache.set(cache_key, response, ttl, now)

            sock.sendto(response_data, client_addr)
            latency = (time.time() - start) * 1000
            # print(
            #     f"[CACHE MISS] {qname} | {latency:.2f} ms "
            #     f"(hits={cache.hits}, misses={cache.misses}, ttl={ttl})"
            # )

            logger.log({
                **base_event,
                "category": category,
                "decision": "ALLOW",
                "cache":"MISS",
                "latency_ms":round(
                    (time.time()-start)*1000, 2
                )
            })

        except Exception as e:
            print(f"[ERROR] {e}")
