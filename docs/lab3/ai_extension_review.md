# AI Extension Review

## Feature

Add a help response that lists the assistant's supported capabilities.

## Review changes

1. The extension uses a typed `Intent.HELP` and the router instead of adding a
   special-case string check to the CLI or returning a magic string.
2. The service returns a deterministic capability list directly; it does not
   call the handbook or responder for a help request.
3. Tests cover the recognized help phrases and verify that the responder is not
   called, protecting the service boundary and keeping the feature offline.

## Verification

The router tests cover `help` and `what can you do?`. The service test checks
that a help request returns the documented capabilities with `degraded=False`.
