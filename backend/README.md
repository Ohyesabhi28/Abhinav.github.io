# Chat backend (AWS Lambda + Amazon Bedrock)

Replaces the free pollinations.ai fallback with your own endpoint. The resume
context lives server-side in `resume_context.txt`, and requests are capped
(8 turns, 500 chars each, 300 output tokens).

## Deploy

1. **Bedrock access:** in the AWS console, open *Amazon Bedrock → Model access* and enable a Claude model
   in your region. The default `MODEL_ID` is `us.anthropic.claude-haiku-4-5-20251001-v1:0`; change it with an
   environment variable if your region uses a different inference-profile ID.
2. **Create the function:** Lambda → *Create function* → Python 3.12. Upload `lambda_function.py` and
   `resume_context.txt` together (zip both files, or paste them into the console editor and add the txt file).
3. **Permissions:** add `bedrock:InvokeModel` (and `bedrock:InvokeModelWithResponseStream` if you stream later)
   to the function's execution role.
4. **Timeout:** raise the timeout to ~20 seconds (default is 3).
5. **Function URL:** *Configuration → Function URL → Create*, auth type `NONE`. Under *CORS*, set:
   - Allow origin: your site (e.g. `https://myself1625.netlify.app`)
   - Allow methods: `POST`
   - Allow headers: `content-type`
6. **Cost guard:** set *reserved concurrency* to something small (e.g. 2) and add an AWS Budget alert, since the
   URL is public.
7. **Wire it up:** paste the Function URL into `CHAT_API_URL` near the chatbot code in `index.html`.

If the backend is unreachable, the site silently falls back to the free endpoint.

## Test locally

```bash
curl -X POST "$FUNCTION_URL" -H "content-type: application/json" \
  -d '{"messages":[{"role":"user","content":"What projects has Abhinav built?"}]}'
```
