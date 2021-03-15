# How to write test cases

- [Understand LISA](#understand-lisa)
- [Document excellence](#document-excellence)
  - [Description in metadata](#description-in-metadata)
  - [Code comments](#code-comments)
  - [Commit messages](#commit-messages)
  - [Logging](#logging)
  - [Error message](#error-message)
  - [Meaningful Assertion](#meaningful-assertion)
- [Troubleshooting excellence](#troubleshooting-excellence)
- [Test code excellence](#test-code-excellence)
  - [Compositions of test](#compositions-of-test)
  - [Metadata](#metadata)
    - [Test suite metadata](#test-suite-metadata)
    - [Test case metadata](#test-case-metadata)
  - [Setup and cleanup](#setup-and-cleanup)
  - [Test body](#test-body)
- [Use components in code](#use-components-in-code)
  - [Environment and node](#environment-and-node)
  - [Tool](#tool)
  - [Scripts](#scripts)
  - [Assertions](#assertions)
  - [Features](#features)
- [Best practices](#best-practices)
  - [Debug test case](#debug-test-case)
  - [Written by non-native English speakers](#written-by-non-native-english-speakers)

Before writing a test case, we strongly recommend that you read the entire document. In addition to how to write test cases, we also believe that the engineering excellence is equally important. After the test case is completed, it will be run thousands of times, and many people will read and troubleshoot it. A good test case can save you and others time.

## Understand LISA

It depends on what kind of contribution on LISA, you may need to understand LISA deeper. Learn more from below topics.

- [Concepts](concepts.md) includes design considerations, how components work together.
- [Development](development.md) includes how to setup environment, code guideline, and others.
- [Extensions](extension.md) includes all extendable components, and how to develop extensions in LISA. In some cases, you may need to implement or improving tools for test cases.

## Document excellence

The documentation is first chance to make things clear, and easy to maintain. A good document doesn't mean more is better. Each kind of documentation has it's own purpose. A good technical document should be *useful and accurate*.

Below introduces the principles for each kind of document in LISA, and provides some extended readings for reference.

### Description in metadata

The description uses to generate test specification. So it should include test purpose, and steps.

- Test suite metadata. A test suite is a couple of test cases, which has similar test purpose, or shared steps. So the metadata should explain why test cases are bundled together.
- Test case metadata. Each test case has its test purpose, and steps. Since the metadata may be read independently, so it needs to document major steps of test logic. If it's a regression test case, it should reference the bug for more reference. It's also good to include the impact, if it fails.

### Code comments

It's a popular topic, and many best practices are valuable to adopt. Here are some highlights.

- Do not repeat code logic. The code comment is not like metadata, since the code comment always stay with code. Don't repeat if/else like if ... else..., don't repeat what already in log strings and exception messages, don't repeat which can be clear from variable names.
- Document for business logic. Code logic is more details than business logic. Some complex code logic may not be intuitive to business logic. The code comments can help summarize a complex code logic.
- Comment on trick things. We cannot avoid take tricks in code sometime. For example, a magic number, a special handling for a Linux version, or something else.
- Provide examples to regular expressions. LISA uses many regular expressions to parse command output. It's simple and useful, but also can be mismatched. When you need to create or update a regex, it needs to check whether there is regression with examples. The examples is also helpful to understand what the expressions do.

### Commit messages

Commit messages uses to explain why makes this change. The code comments describe the current status. The commit messages describe the reason of change. If the content is also suitable in the code, then move it to code comments.

### Logging

The logging is for two purposes, 1) show the progress, 2) troubleshooting.

To show the progress, the log should be simple and logical. For troubleshooting, it needs more detailed information. It sounds conflict goals, but they can be achieved by different INFO and DEBUG. LISA is always DEBUG level in file, and INFO level on console by default.

- **DEBUG** level log should provide *right level* details. To write with *right level*, the only way is to use it from beginning.

  Keep to use and improve log when writing code. If you need to debug step by step, it means the log need to be improved. If you don't understand what the log meaning, refine it. If you find duplicate information, merge it.

- **INFO** level log should be *like a story*, to tell what happens.

  It's what you want to know every time, even the whole progress is smooth. It should be friendly, so that new users can understand what happening. It should be as less as possible. It should tell user to waiting some long time operation.

- **WARNING** level log should be avoid.

  The warning message means something important, but no need to stop. But in most cases, you will find either it's not so important than the info level, or it's so important to stop run.

  When I'm writing this document, there are 3 warning messages in LISA. After reviewed, I converted all of them to info or error. There is only one left, is up to user to suppress exceptions.
- **ERROR** level log should be reviewed carefully.

  Error level logs help finding potential problems. If there are too much error level logs, it will hide important problems. In a happy run, there shouldn't be error level log. By a thumb rule, 95% succeed runs shouldn't have any error level logs.

Tips,

- The log explains things itself, not depends on code. So the log describes business logic, not code logic. A bad example, "4 items found: [a , b , c]", should be "found 4 channels, merged names: [a, b, c]".
- Make every line of log is unique in code. If we have to see where the log is printed in code. We can locate the code quickly by searching. A bad example, `log.info("received stop signal")`, should be `log.info("received stop signal in lisa_runner")`.
- Don't repeat similar lines continually. It's worth to add logic and variables to reduce redundant logs.
- Reduce lines of log. If two lines of log alway appear together, merge them to one line. Lines of log affect the readability more than width of log. The log can be wrapped.
- Correlate logs by context, especially there is concurrency. A bad example, "cmd: echo hello world", "cmd: hello world" can be "cmd[666]: echo hello world", "cmd[666]: hello world".

### Error message

There are two kinds of error messages in LISA. First is an error message doesn't fail the case, it's printed in stderr, and will be looked when a test case failed. Second is a one line message in failed test case. This section applies to two of them, but second one is more important, since we hope it's the only needed information to help understanding a failed test case.

In LISA, failed, and skipped test cases have a message. It specifies the reason, why this test cases is failed or skipped. With this message, users can understand what happens, and may take actions. So this message should be helpful as much as possible.

The error message should include what happens, and how to fix it. It may not easy to provide all situations at first time, but guesses are also helpful. At the same time, the raw error message is also helpful, don't hide it.

For examples,

- "cannot find subscription id [aaa], make sure exists and current account can access". A bad example, "cannot find subscription id [aaa]". It says what happens technically, it should provide more suggestions.
- "cannot find vm size [aaa] on location [bbb], it may cause by this vm size is unavailable in this location.". A bad example, "cannot find vm size [aaa] on location [bbb]". It says what happens, but doesn't provide guesses on root cause.

### Meaningful Assertion

Assertions are used a lot in test code. The assertions are simple patterns of `if some check fails, then throw an exception`.

An assertion library includes common used patterns, and detailed error messages. LISA uses assertpy as standard assertion library, which provides Pythonic and test friendly assertions.

When writing assertions,

- Put actual value in `assert_that`, so that the style is consistent, and one actual value can be assert multiple times in one expression.
- Assert as much comprehensive as possible, but not repeat asserted already. For example, `assert_that(str1).is_equal_to('hello')` is enough, no need like `assert_that(str1).is_instance_of(str).is_equal_to('hello')`.
- Add description to explain the business logic. For example, `assert_that(str1).described_as('echo back result is unexpected').is_equal_to('hello')` is better than `assert_that(str1).is_equal_to('hello')`.
- Try to use native assertion instead of operating data your self. `assert_that(vmbuses).is_length(6)` is better than `assert_that(len(vmbuses)).is_equal_to(6)`. It's more simple, and error message is more clear.
- Don't forget to use powerful collection assertions. They can compare ordered list, `contains` (actual value is superset), `is_subset_of` (actual value is subset), ``.

Learn more from LISA code and [assertpy document](https://github.com/assertpy/assertpy#readme).

## Troubleshooting excellence

Test failure is a common occurrence. So troubleshooting the failure happens often too. There are serval ways used to troubleshoot the failures, and the top ones is better than bottom ones, since it's lower cost to analyze.

1. One line message. The one line message is delivered with test result status. If the root cause can be addressed by this message, it doesn't need any extra effort to understand the reason. Even there can be some automation to match the message and take actions.
2. Test case log. LISA provides the whole log, it includes outputs from all test cases, all threads and all node outputs. This file can be regarded as default log, which is easy to search.
3. Other log files. There are some original logs, or split to test cases. It's more easier to view, when the issue is narrow down.
4. Repro in an environment. It's high cost, but contains most information. But sometime, the issue is not able to repro.

In LISA, the test cases fail by Exceptions, and the exception message is regarded as the one line error message. When writing test cases, it's right time to tune the exception messages. When the test case is done, many errors are explained itself well.

## Test code excellence

Your code is the example to others, and they will follow your approach. So, any good and bad practice will be amplified.

In LISA, the test code should be organized by business logic. It means that the code should like a test spec to demonstrate the test purpose. The underlying logic should be implemented in other places, like tools, features or private methods in test suite.

Be careful on using sleep! The only way to use sleep, is in a poll mode. It means you have to wait something by checking periodically. In the loop of checking, it can have a sleep to wait a reasonable period. Never wait something like sleep 10 seconds. It causes two problems, 1) if it's too short in some scenario, the case may fail, 2) if it's long enough, it slows down the test run.

### Compositions of test

A LISA test composes by metadata, setup/cleanup, and test body.

### Metadata

The metadata uses to provide document, and settings for test suite and test cases.

#### Test suite metadata

- **area** catalogs test suites by belonging. When it needs to have a special validation on some area, it can be used to filter test cases. The values can be provisioning, cpu, memory, storage, network, etc.
- **category** catalogs test case by it's test type. It includes functional, performance, stress and community. The performance and stress test cases spend longer time to run, it's not included in usual runs. The community test cases is wrappers, it helps to provide comparable results with community.
- **description** should introduce this test suite, including the purpose, coverage and anything else, which helps knowing this test suite.
- **name** is optional. The default name is class name, and can be replaced by the name field. The name is the part of test name. It's like the namespace in program languages.
- **requirement** defines the default requirement for this test suite, and can be overwritten in test case level. Learn more from [concepts](concepts.md).

See example for details.

```python
@TestSuiteMetadata(
    area="provisioning",
    category="functional",
    description="""
    This test suite uses to verify if an environment can be provisioned correct or not.

    - The basic smoke test can run on all images to determinate if a image can boot and
    reboot.
    - Other provisioning tests verify if an environment can be provisioned with special
    hardware configurations.
    """,
)
class Provisioning(TestSuite):
    ...
```

#### Test case metadata

- **priority** is determined by test case impact, and uses to decide how often to run the case. Learn more from [concepts](concepts.md).
- **description** explain the test purpose and steps. It uses to generate test specification document.
- **requirement** defines the requirement of this case. If requirement is not specified, the default requirement of test suite or the global default requirement will be used.

See example for details.

```python
@TestCaseMetadata(
    description="""
    This case verifies whether a node is operating normally.

    Steps,
    1. Connect to TCP port 22. If it's not connectable, failed and check whether
        there is kernel panic.
    2. Connect to SSH port 22, and reboot the node. If there is an error and kernel
        panic, fail the case. If it's not connectable, also fail the case.
    3. If there is another error, but not kernel panic or tcp connection, pass with
        warning.
    4. Otherwise, fully passed.
    """,
    priority=0,
    requirement=simple_requirement(
        environment_status=EnvironmentStatus.Deployed,
        supported_features=[SerialConsole],
    ),
)
def smoke_test(self, case_name: str) -> None:
    ...
```

### Setup and cleanup

There are two couples methods: 1) before_suite, after_suite and 2) before_case, after_case. They will be called on corresponding steps. When writing test cases, they are used to share common logic or variables.

### Test body

It's the logic of a test case. Learn more from [test code excellence](#test-code-excellence) and learn how to use below LISA components to speed up development.

## Use components in code

LISA wraps shared logic in below components. When implementing test cases, you may need to a new component, and you are welcome to contribute it.

### Environment and node

### Tool

### Scripts

### Assertions

### Features

## Best practices

### Debug test case

in ready environment

### Written by non-native English speakers
