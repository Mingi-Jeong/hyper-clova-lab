from hcx_eval.ids import RequestIdentity, RunIdentity, make_request_id, make_run_id


def test_run_and_request_ids_are_stable_and_input_sensitive() -> None:
    # Given: one reproducibility identity and two request attempts.
    run_identity = RunIdentity(
        run_seed="approved-smoke-1",
        config_sha256="a" * 64,
        dataset_sha256="b" * 64,
        docs_snapshot_sha256="c" * 64,
    )
    run_id = make_run_id(run_identity)
    first = RequestIdentity(
        run_id=run_id, case_id="FAQ-0001", model="HCX-005", attempt=0
    )
    retry = first.model_copy(update={"attempt": 1})

    # When: IDs are derived repeatedly from the same typed inputs.
    repeated_run_id = make_run_id(run_identity)
    repeated_request_id = make_request_id(first)

    # Then: identical inputs are stable and a retry has a distinct identity.
    assert repeated_run_id == run_id
    assert repeated_request_id == make_request_id(first)
    assert make_request_id(retry) != repeated_request_id
