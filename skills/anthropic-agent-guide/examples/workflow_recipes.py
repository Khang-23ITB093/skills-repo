#!/usr/bin/env python3
"""
workflow_recipes.py - Các mẫu hình Dynamic Workflow bằng Python
Minh họa 3 mẫu hình:
1. Fan-out and Synthesize với chính sách PARTIAL_FAILURE_POLICY
2. Adversarial Verification (Worker + Skeptic Verifier)
3. Pairwise Tournament Ranking (So sánh đối đầu)
"""

import asyncio
import sys
from typing import Dict, Any, List

# Cấu hình UTF-8 cho Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ==============================================================================
# PATTERN 1: Fan-out and Synthesize kèm PARTIAL_FAILURE_POLICY
# ==============================================================================

async def mock_worker_subagent(task_id: str, payload: str, should_fail: bool = False) -> Dict[str, Any]:
    """Mô phỏng một subagent thực thi độc lập trên một context window sạch."""
    await asyncio.sleep(0.05)
    if should_fail:
        return {
            "task_id": task_id,
            "status": "error",
            "result": None,
            "error_msg": f"Subagent for {task_id} encountered timeout or API error."
        }
    return {
        "task_id": task_id,
        "status": "ok",
        "result": f"Analysis completed for {payload}: No critical vulnerabilities found.",
        "error_msg": None
    }


async def fanout_and_synthesize(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Chạy song song các tasks con và tổng hợp kết quả theo chính sách PARTIAL_FAILURE_POLICY:
    - Nếu > 50% thất bại -> Abort và raise Exception.
    - Nếu <= 50% thất bại -> Tổng hợp partial results và gắn nhãn [INCOMPLETE_DATA].
    """
    coroutines = [
        mock_worker_subagent(t["id"], t["payload"], t.get("fail", False))
        for t in tasks
    ]
    raw_results = await asyncio.gather(*coroutines, return_exceptions=False)

    success_results = []
    failed_tasks = []

    for r in raw_results:
        if r["status"] == "ok":
            success_results.append(r)
        else:
            failed_tasks.append(r)

    total = len(tasks)
    fail_rate = len(failed_tasks) / total if total > 0 else 0

    if fail_rate > 0.5:
        raise RuntimeError(
            f"PARTIAL_FAILURE_POLICY: Quá nhiều subagents thất bại ({len(failed_tasks)}/{total} = {fail_rate:.1%}). "
            "Toàn bộ tác vụ bị hủy bỏ để đảm bảo an toàn dữ liệu."
        )

    # Tổng hợp kết quả
    is_incomplete = len(failed_tasks) > 0
    report_tag = "[INCOMPLETE_DATA]" if is_incomplete else "[COMPLETE]"

    return {
        "tag": report_tag,
        "total_tasks": total,
        "success_count": len(success_results),
        "failed_count": len(failed_tasks),
        "synthesized_findings": [item["result"] for item in success_results],
        "missing_items": [item["task_id"] for item in failed_tasks]
    }


# ==============================================================================
# PATTERN 2: Adversarial Verification (Worker + Skeptic Verifier)
# ==============================================================================

async def adversarial_verification(proposed_solution: str, rubric: str) -> Dict[str, Any]:
    """Worker đề xuất giải pháp, Skeptic Verifier độc lập phản biện dựa trên rubric."""
    await asyncio.sleep(0.05)
    # Skeptic agent phân tích độc lập
    skeptic_critique = {
        "verdict": "pass",
        "potential_risks": ["Cần bảo đảm lockfile không bị trôi version"],
        "confidence": "high"
    }
    return {
        "solution": proposed_solution,
        "rubric_applied": rubric,
        "verification": skeptic_critique
    }


# ==============================================================================
# UTILITY: Pre-check Cost Estimation & Exponential Backoff
# ==============================================================================

PRICE_TABLE = {
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-opus-5-5": (4.0, 20.0),
    "claude-haiku-4-5-20251001": (1.0, 5.0),
    "claude-sonnet-5-5": (2.0, 10.0),
}

def estimate_cost(input_tokens: int, output_tokens: int, model_id: str) -> float:
    """Ước lượng chi phí USD trước khi chạy một workflow tốn kém."""
    pin, pout = PRICE_TABLE.get(model_id, (3.0, 15.0))
    return round((input_tokens * pin + output_tokens * pout) / 1e6, 5)


async def call_with_backoff(func, *args, max_retries: int = 3, base_delay: float = 0.5, **kwargs):
    """Bọc lời gọi API với Exponential Backoff & Jitter để chống Rate Limit."""
    import random
    retries = 0
    while True:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            retries += 1
            if retries > max_retries:
                raise e
            delay = base_delay * (2 ** (retries - 1)) + random.uniform(0, 0.1)
            await asyncio.sleep(delay)


# ==============================================================================
# PATTERN 3: Pairwise Tournament (Thi đấu đối đầu xếp hạng)
# ==============================================================================

async def compare_pair(candidate_a: str, candidate_b: str, criteria: str) -> str:
    """Judge agent so sánh 2 phương án đối đầu với deterministic tie-break."""
    await asyncio.sleep(0.02)
    # So sánh độ dài: ngắn hơn thắng
    if len(candidate_a) < len(candidate_b):
        return candidate_a
    elif len(candidate_b) < len(candidate_a):
        return candidate_b
    # Deterministic tie-break: chọn theo thứ tự alphabet để tránh vòng lặp vô tận
    return candidate_a if candidate_a <= candidate_b else candidate_b


async def run_tournament(candidates: List[str], criteria: str) -> str:
    """Chạy giải đấu loại trực tiếp từng cặp để tìm ra người chiến thắng."""
    if not candidates:
        return ""
    current_round = candidates[:]
    while len(current_round) > 1:
        next_round = []
        for i in range(0, len(current_round), 2):
            if i + 1 < len(current_round):
                winner = await compare_pair(current_round[i], current_round[i+1], criteria)
                next_round.append(winner)
            else:
                next_round.append(current_round[i])
        current_round = next_round
    return current_round[0]


# ==============================================================================
# DEMO EXECUTION
# ==============================================================================

async def demo():
    print(">>> 1. Chạy Fan-out & Synthesize (Thử nghiệm 4 tasks, 1 lỗi <= 50%)...")
    tasks = [
        {"id": "auth.py", "payload": "Module Auth"},
        {"id": "pay.py", "payload": "Module Payment"},
        {"id": "db.py", "payload": "Module Database", "fail": True},
        {"id": "api.py", "payload": "Module API"},
    ]
    res = await fanout_and_synthesize(tasks)
    print(f"    Kết quả: Tag={res['tag']} | Thành công={res['success_count']}/{res['total_tasks']}")
    print(f"    Thiếu: {res['missing_items']}")

    print("\n>>> 2. Chạy Adversarial Verification...")
    adv_res = await adversarial_verification("Nâng cấp thư viện auth v2.1", "Zero breaking change")
    print(f"    Skeptic Verdict: {adv_res['verification']['verdict']}")

    print("\n>>> 3. Chạy Pairwise Tournament (với tie-break xác định)...")
    candidates = ["auth_jwt", "auth_jwt", "check_login"]
    best = await run_tournament(candidates, "Ngắn gọn và rõ ràng nhất")
    print(f"    Phương án chiến thắng: {best}")

    print("\n>>> 4. Tiền kiểm tra chi phí (Estimate Cost)...")
    cost_est = estimate_cost(input_tokens=25000, output_tokens=4000, model_id="claude-sonnet-4-6")
    print(f"    Ước tính chi phí task 25k in / 4k out trên Sonnet 4.6: ${cost_est:.5f} USD")


if __name__ == "__main__":
    asyncio.run(demo())
