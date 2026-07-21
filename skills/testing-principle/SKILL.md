---
name: testing-principle
description: Apply this repository's pytest testing principles whenever writing, revising, or reviewing Python tests. Prefer real collaborators, behavior-focused test classes, parametrized cases, reusable fixtures, mirrored unit-test paths, and public-interface assertions while directly testing critical private logic when warranted.
---

# Testing Principle

Write pytest tests that maximize confidence and survive refactoring. Optimize for realistic behavior and readability before test speed or isolation.

## Process

1. Locate the source module and its public interface, then classify the test as unit or integration. Mirror unit tests under `tests/unit`; for example, `src/acme/webhooks/sender.py` maps to `tests/unit/acme/webhooks/test_sender.py`. Place integration tests under `tests/integration` according to the boundary or workflow they exercise.
2. Identify observable behaviors, failure modes, and input boundaries. Group related tests in behavior-named classes such as `TestWebhookFail`; do not use test classes merely to share setup.
3. Choose the most real execution path practical. Use real domain objects and in-process implementations even when they make the test more expensive. Replace a collaborator only at a boundary that is unavailable, destructive, nondeterministic, or prohibitively costly, and prefer a small fake or local test implementation over interaction-heavy mocks. For a path that can call a hosted LLM and consume billed or quota tokens, register an explicit `--run-live-llm` pytest option and use a fixture to select the provider: without the flag, return a deterministic mocked LLM response that exercises parsing and downstream behavior; with the flag, call the real LLM through the same interface. Run the test in both modes rather than skipping it by default.
4. Move complex or repeated construction into fixtures. Give each fixture the narrowest scope that safely matches the object's lifecycle: function for mutable or stateful objects, class or module for safely shared expensive setup, and session only for immutable or explicitly resettable resources. Use factory fixtures when cases need several variants.
5. Collapse cases with identical behavior into `pytest.mark.parametrize`. Include normal, boundary, empty, invalid, and regression inputs as relevant; add readable `ids` when raw values do not explain the case. Keep separate tests when setup, action, or expected behavior materially differs.
6. Assert through the public interface and on externally observable outcomes by default. Avoid assertions tied to call order, internal representation, or incidental implementation details. Directly test private logic only when it is critical, has meaningful complexity or safety impact, and cannot be covered precisely enough through the public interface; keep such tests few and acknowledge the tighter coupling in the test name or a short comment.
7. Run the narrowest relevant pytest target, then inspect the collected node IDs to confirm the file, class, and parametrized cases are easy to find and trigger.

## Rules

- Real objects are the default; mocks require a concrete boundary reason. Test runtime alone is not sufficient reason to mock.
- The `--run-live-llm` flag switches only the LLM boundary: default runs use a representative mocked response, while flagged runs use the real provider.
- Prefer state and result assertions over mock interaction assertions.
- A test class represents one behavior or scenario, not the production class. Keep it stateless and omit `__init__`.
- Parametrize data variations, not unrelated behaviors.
- Fixtures hide construction noise, not the behavior under test. Keep the important action and assertions visible in each test.
- Broader fixture scope is valid only when isolation remains explicit and reliable.
- Mirror source paths under `tests/unit` so a developer can infer either file's location from the other.
- Most tests target public contracts; critical private tests are deliberate exceptions, not a shortcut around awkward public behavior.

## Completion check

Before finishing, verify every new or changed test:

- uses real collaborators unless its replacement has a stated boundary reason;
- runs every LLM-dependent test with a mocked response by default and switches the same test to the real provider only with `--run-live-llm`;
- sits in `tests/unit` at the mirrored source path, or in `tests/integration` for a boundary-spanning test, and uses a behavior-named class where related cases exist;
- uses parametrization for genuine input variations;
- moves complex repeated setup into correctly scoped fixtures;
- primarily asserts public, observable behavior;
- keeps any private-logic coverage narrowly justified; and
- passes when run by file and by its class or node ID.
