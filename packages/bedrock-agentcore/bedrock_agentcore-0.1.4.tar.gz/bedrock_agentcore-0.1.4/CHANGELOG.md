# Changelog

## [0.1.4] - 2025-09-17

### Added
- feat: implement AWS Lambda compatible JSON logging (#76) (114a670)

### Fixed
- fix: dont use milliseconds or microseconds because boto3 doesnt suppo… (#83) (5b97e5a)

### Other Changes
- ci(deps): bump actions/setup-python from 5 to 6 (#73) (df70612)
- add optional session parameter to CodeInterpreter for custom credential management (#41) (fa8b028)
- ci(deps): bump trufflesecurity/trufflehog from 3.90.2 to 3.90.6 (#72) (458c8dc)
- ci(deps): bump aws-actions/configure-aws-credentials from 4 to 5 (#71) (503bbda)
- ci(deps): bump actions/checkout from 4 to 5 (#55) (094a182)
- ci(deps): bump actions/download-artifact from 4 to 5 (#48) (f2831d3)
- Release v0.1.3 (#70) (b1eab20)

## [0.1.3] - 2025-09-05

### Added
- fix/observability logs improvement (#67) (78a5eee)
- feat: add AgentCore Memory Session Manager with Strands Agents (#65) (7f866d9)
- feat: add validation for browser live view URL expiry timeout (#57) (9653a1f)

### Other Changes
- feat(memory): Add passthrough for gmdp and gmcp operations for Memory (#66) (1a85ebe)
- Improve serialization (#60) (00cc7ed)
- feat(memory): add functionality to memory client (#61) (3093768)
- add automated release workflows (#36) (045c34a)
- chore: remove concurrency checks and simplify thread pool handling (#46) (824f43b)
- fix(memory): fix last_k_turns (#62) (970317e)
- use json to manage local workload identity and user id (#37) (5d2fa11)
- fail github actions when coverage threshold is not met (#35) (a15ecb8)

## [0.1.2] - 2025-08-11

### Fixed
- Remove concurrency checks and simplify thread pool handling (#46)

## [0.1.1] - 2025-07-23

### Fixed
- **Identity OAuth2 parameter name** - Fixed incorrect parameter name in GetResourceOauth2Token
  - Changed `callBackUrl` to `resourceOauth2ReturnUrl` for correct API compatibility
  - Ensures proper OAuth2 token retrieval for identity authentication flows

- **Memory client region detection** - Improved region handling in MemoryClient initialization
  - Now follows standard AWS SDK region detection precedence
  - Uses explicit `region_name` parameter when provided
  - Falls back to `boto3.Session().region_name` if not specified
  - Defaults to 'us-west-2' only as last resort

- **JSON response double wrapping** - Fixed duplicate JSONResponse wrapping issue
  - Resolved issue when semaphore acquired limit is reached
  - Prevents malformed responses in high-concurrency scenarios

### Improved
- **JSON serialization consistency** - Enhanced serialization for streaming and non-streaming responses
  - Added new `_safe_serialize_to_json_string` method with progressive fallbacks
  - Handles datetime, Decimal, sets, and Unicode characters consistently
  - Ensures both streaming (SSE) and regular responses use identical serialization logic
  - Improved error handling for non-serializable objects

## [0.1.0] - 2025-07-16

### Added
- Initial release of Bedrock AgentCore Python SDK
- Runtime framework for building AI agents
- Memory client for conversation management
- Authentication decorators for OAuth2 and API keys
- Browser and Code Interpreter tool integrations
- Comprehensive documentation and examples

### Security
- TLS 1.2+ enforcement for all communications
- AWS SigV4 signing for API authentication
- Secure credential handling via AWS credential chain
