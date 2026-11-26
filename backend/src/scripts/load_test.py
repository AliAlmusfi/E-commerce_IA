import requests

PRODUCT_ID = 550
# USER_ID = 2


session = requests.Session()
session.headers.update({
    "Accept": "application/json",
})


def get_payload()->dict:
    return {
        "items":[
            {
                "product_id": PRODUCT_ID,
                "quantity": 1
            }
        ]
    }
def get_token()->str:
    res= session.post("http://localhost:80/api/v1/users/token/", json={
        "email": "maroof95at@gmail.com",
        "password": "12345678"
    }, timeout=15)
    if res.status_code == 200:
        return res.json()['access']
    else:
        print(f"Couldn't get authentication token !! [{res.status_code}]: {res.text}")
        return "eInvalidToken"

session.headers.update({
    "Authorization": f"Bearer {get_token()}",
    "Accept": "application/json",
})


payload = get_payload()
successful_creations = 0;
failed_creations = 0;
for _ in range(500):
    resp = session.post("http://localhost:80/api/v1/orders/", json=payload, timeout=100)
    if resp.ok:
        successful_creations += 1
        print(f"Order {_} Created")
        print(resp.json())
    else:
        failed_creations += 1
        print(f"Failed: [{resp.status_code}]: " + resp.text)

    # r.raise_for_status()


print(f"Successful Creations: {successful_creations}")
print(f"Failed Creations: {failed_creations}")









# #!/usr/bin/env python3
# """
# load_test.py — Concurrent authenticated load test against the e-commerce API.

# Examples:
#     # 500 total requests, 20 concurrent
#     python load_test.py --total 500 --concurrency 20

#     # Target the list endpoint instead of create
#     python load_test.py --total 500 --endpoint list

#     # Ramp: 10 users doing 50 requests each
#     python load_test.py --users 10 --per-user 50 --concurrency 10
# """
# import argparse
# import statistics
# import sys
# import time
# from collections import Counter
# from concurrent.futures import ThreadPoolExecutor, as_completed

# import requests


# # ------------------------------------------------------------------ auth

# def login(base_url: str, email: str, password: str) -> str:
#     r = requests.post(
#         f"{base_url}/api/token/",
#         json={"email": email, "password": password},
#         timeout=10,
#     )
#     r.raise_for_status()
#     return r.json()["access"]


# # ------------------------------------------------------------- requests

# def create_order(base_url, token, product_id, quantity=1):
#     headers = {"Authorization": f"Bearer {token}"}
#     payload = {"items": [{"product_id": product_id, "quantity": quantity}]}
#     t0 = time.perf_counter()
#     try:
#         r = requests.post(
#             f"{base_url}/api/v1/orders/",
#             json=payload,
#             headers=headers,
#             timeout=30,
#         )
#         return r.status_code, (time.perf_counter() - t0) * 1000, r.text[:200]
#     except Exception as e:
#         return 0, (time.perf_counter() - t0) * 1000, f"{type(e).__name__}: {e}"[:200]


# def list_orders(base_url, token):
#     headers = {"Authorization": f"Bearer {token}"}
#     t0 = time.perf_counter()
#     try:
#         r = requests.get(
#             f"{base_url}/api/v1/orders/",
#             headers=headers,
#             timeout=30,
#         )
#         return r.status_code, (time.perf_counter() - t0) * 1000, r.text[:200]
#     except Exception as e:
#         return 0, (time.perf_counter() - t0) * 1000, f"{type(e).__name__}: {e}"[:200]


# # ------------------------------------------------------------------ main

# def run_task(args, token, idx):
#     if args.endpoint == "create":
#         return create_order(args.base_url, token, args.product_id, args.quantity)
#     return list_orders(args.base_url, token)


# def percentile(values, p):
#     if not values:
#         return 0.0
#     values = sorted(values)
#     k = max(0, min(len(values) - 1, int(round((p / 100) * (len(values) - 1)))))
#     return values[k]


# def main():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--base-url", default="http://localhost")
#     ap.add_argument("--email", required=True, help="Login email of a seeded user")
#     ap.add_argument("--password", required=True)
#     ap.add_argument("--total", type=int, default=500, help="Total requests")
#     ap.add_argument("--concurrency", type=int, default=20, help="Parallel workers")
#     ap.add_argument("--endpoint", choices=["create", "list"], default="create")
#     ap.add_argument("--product-id", type=int, required=False, help="Required for create")
#     ap.add_argument("--quantity", type=int, default=1)
#     args = ap.parse_args()

#     if args.endpoint == "create" and args.product_id is None:
#         print("ERROR: --product-id is required for --endpoint create", file=sys.stderr)
#         sys.exit(1)

#     print(f"→ Logging in to {args.base_url} as {args.email} ...")
#     token = login(args.base_url, args.email, args.password)
#     print(f"  Got JWT (length={len(token)})")

#     results = []
#     t_start = time.perf_counter()

#     print(f"→ Firing {args.total} requests with {args.concurrency} workers …")
#     with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
#         futures = [pool.submit(run_task, args, token, i) for i in range(args.total)]
#         for i, fut in enumerate(as_completed(futures), 1):
#             status, latency_ms, body = fut.result()
#             results.append((status, latency_ms, body))
#             if i % 50 == 0 or i == args.total:
#                 print(f"  {i}/{args.total} done")

#     elapsed = time.perf_counter() - t_start
#     latencies = [r[1] for r in results]
#     statuses = Counter(r[0] for r in results)
#     ok = statuses.get(200, 0) + statuses.get(201, 0)
#     failed = args.total - ok

#     print("\n" + "=" * 60)
#     print(f"Total requests : {args.total}")
#     print(f"Elapsed        : {elapsed:.2f} s")
#     print(f"Throughput     : {args.total / elapsed:.1f} req/s")
#     print(f"Success        : {ok}  ({ok / args.total:.1%})")
#     print(f"Failed         : {failed}")
#     print("-" * 60)
#     print("Status codes:")
#     for code, n in sorted(statuses.items()):
#         print(f"  {code:>4}  × {n}")
#     print("-" * 60)
#     print(f"Latency (ms) — min={min(latencies):.1f}  "
#           f"mean={statistics.mean(latencies):.1f}  "
#           f"p50={percentile(latencies, 50):.1f}  "
#           f"p95={percentile(latencies, 95):.1f}  "
#           f"p99={percentile(latencies, 99):.1f}  "
#           f"max={max(latencies):.1f}")
#     print("=" * 60)

#     if failed:
#         print("\nSample errors:")
#         for status, _, body in results:
#             if status not in (200, 201):
#                 print(f"  [{status}] {body[:160]}")
#                 break

#     sys.exit(0 if failed == 0 else 1)


# if __name__ == "__main__":
#     main()