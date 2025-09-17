# LLM APIs

Denario requires access to large language models (LLMs) to function. Currently, Denario supports LLMs from [Google (Gemini series)](https://ai.google.dev/gemini-api/docs/models?hl=es-419), [OpenAI (GPT and o series)](https://platform.openai.com/docs/models), [Anthropic (Claude)](https://www.anthropic.com/claude), [Perplexity (Sonar)](https://sonar.perplexity.ai/), and agents from [Futurehouse (Owl)](https://platform.futurehouse.org/). Access to all these models is not mandatory for experimentation; however, **at least OpenAI API access is required for the Analysis module**, so an OpenAI API key must be configured if that module is expected to be employed.

API access is managed via keys generated on each provider's platform and set as environment variables. Most LLM providers require a small amount of credit to be added to your account, as usage typically incurs a cost (though this is relatively minor for experimentation).

The table below summarizes which LLM models are required (✅), optional (🟠) or not employed (❌) for each of the Denario modules:

| Subsystem          | OpenAI | Gemini | Vertex AI | Claude | Perplexity | FutureHouse |
| ------------------ | ------ | ------ | --------- | ------ | ---------- | ----------- |
| **Generate Ideas** | 🟠     | 🟠     | 🟠        | 🟠     | ❌         | ❌          |
| **Methods**        | 🟠     | 🟠     | 🟠        | 🟠     | ❌         | ❌          |
| **Analysis**       | ✅     | 🟠     | 🟠        | 🟠     | ❌         | ❌          |
| **Paper Writing**  | 🟠     | 🟠     | ❌        | 🟠     | ❌         | ❌          |
| Citation Search    | ❌     | ❌     | ❌        | ❌     | ✅         | ❌          |
| Check Idea         | 🟠     | 🟠     | 🟠        | 🟠     | 🟠         | ✅          |

## Quick Navigation

- **[How Much Money Is Needed?](how-much-money.md)** - Cost estimates and budgeting information
- **[Risk of Overspending](risk-overspending.md)** - Important precautions and monitoring tips
- **[Rate Limits](rate-limits.md)** - Understanding and managing API rate limits
- **[Obtaining API Keys](obtaining-api-keys.md)** - Step-by-step guides for each provider
- **[Vertex AI Setup](vertex-ai-setup.md)** - Detailed setup for Google Cloud Vertex AI
- **[FutureHouse](futurehouse.md)** - Setup for FutureHouse Owl agent
- **[Where to Store API Keys](where-to-store-api-keys.md)** - Environment variable configuration
