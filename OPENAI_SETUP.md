# OpenAI API Setup Guide

## CRITICAL: Required for Application to Function

This application **REQUIRES** OpenAI's DALL-E 3 API to generate unique news images for each article headline.

**⚠️ The application will NOT run without a valid OpenAI API key.**

## Getting Your API Key

1. **Sign up for OpenAI**:
   - Go to https://platform.openai.com/signup
   - Create an account or log in

2. **Get API Key**:
   - Navigate to https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (starts with ``)
   - **Save it securely** - you won't see it again

3. **Add Billing**:
   - Go to https://platform.openai.com/account/billing
   - Add a payment method
   - DALL-E 3 pricing: ~$0.04 per 1024x1024 image
   - **Billing is required** for DALL-E 3 API access

## Local Development Setup

**MANDATORY** - Set the environment variable before running:

```bash
# Linux/Mac
export OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
uvicorn app.main:app --reload

# Windows (Command Prompt)
set OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
uvicorn app.main:app --reload

# Windows (PowerShell)
$env:OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
uvicorn app.main:app --reload
```

**Without this key, the application will crash with:**
```
RuntimeError: OPENAI_API_KEY environment variable is required for AI image generation.
```

## Production Deployment (Render)

1. Go to your Render dashboard
2. Select your web service
3. Click "Environment" tab
4. Add environment variable:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: `YOUR_OPENAI_API_KEY_HERE`
5. Click "Save Changes"
6. Service will automatically redeploy

**⚠️ Deployment will fail without this environment variable.**

## Image Generation Behavior

### When Images Are Generated

- **RSS has image** → Use RSS image (no API call, free)
- **RSS has no image** → Generate AI image from headline (API call, ~$0.04)

### Automatic Update for Existing Articles

**New Feature:** Articles with default placeholder images are automatically updated.

- If article exists with `/static/default-news.jpg`
- On next RSS fetch, system will:
  1. Check for RSS image
  2. If no RSS image, generate AI image
  3. Update the existing article (no duplicate)
  4. Commit to database

### Image Caching

- Generated images are **cached permanently** in the database
- Each article gets **one image only** (never regenerated unless it has default image)
- No API calls for existing articles with real images
- **Migration:** Existing default images will be replaced with AI-generated images

### Cost Estimation

**Initial Deployment (with existing default images):**
- If 40 cached articles have default images
- One-time cost: 40 × $0.04 = **$1.60**

**Ongoing Costs:**
- With default settings (4 categories, 10 articles each)
- **RSS images used when available** (majority of cases, free)
- **Only generates for articles missing images**
- Typical cost per 12-hour cycle: **$0.20-$0.40**
- Maximum cost per cycle: **$1.60** (if no RSS images available)

### Error Handling

**Missing API Key:**
```
RuntimeError: OPENAI_API_KEY environment variable is required for AI image generation.
```
→ Application will not start

**Generation Failure:**
```
RuntimeError: Failed to generate AI image for headline '{headline}': {error}
```
→ Check API key, billing, and rate limits

**No Silent Fallback:** The application will NOT silently use default images if generation fails. It will raise explicit errors.

## Security Best Practices

- ✅ Never commit API keys to Git
- ✅ Use environment variables only
- ✅ Rotate keys periodically
- ✅ Monitor usage at https://platform.openai.com/usage
- ✅ Set spending limits in OpenAI dashboard

## Troubleshooting

### Application Won't Start

**Error:** `RuntimeError: OPENAI_API_KEY environment variable is required`

**Solutions:**
1. Verify environment variable is set: `echo $OPENAI_API_KEY`
2. Restart terminal/shell after setting variable
3. For Render: Check Environment tab has the variable
4. Verify key starts with ``

### "Invalid API Key" Error

**Solutions:**
1. Verify key at https://platform.openai.com/api-keys
2. Regenerate key if needed
3. Update environment variable
4. Restart application

### "Rate Limit Exceeded"

**Solutions:**
- OpenAI has rate limits (5 images/minute for DALL-E 3)
- Wait 1 minute and retry
- Failed generations will raise errors (no silent fallback)

### "Insufficient Credits"

**Solutions:**
1. Check billing at https://platform.openai.com/account/billing
2. Add payment method if missing
3. Add credits to account
4. Verify payment method is valid

### High Costs

**Solutions:**
1. Monitor OpenAI dashboard usage page
2. Most articles should use RSS images (free)
3. Set monthly spending limits in OpenAI settings
4. Check if RSS feeds are providing images

## Migration from Default Images

If your database has articles with `/static/default-news.jpg`:

1. **Set `OPENAI_API_KEY`** in environment
2. **Deploy/restart application**
3. **Wait for next scheduled RSS fetch** (12 hours) or trigger manually
4. **Articles will automatically update** with AI-generated images
5. **One-time cost** for all existing default images

## Cost Control Recommendations

1. **Set OpenAI spending limits**:
   - Go to https://platform.openai.com/account/limits
   - Set monthly budget cap
   - Enable email alerts

2. **Monitor usage**:
   - Check https://platform.openai.com/usage regularly
   - Review costs vs. number of images generated
   - Verify RSS feeds are providing images when possible

3. **Expected costs for 10 users**:
   - Initial migration: ~$1.60 (one-time)
   - Daily ongoing: ~$0.20-$0.80
   - Monthly: ~$6-$24 (depends on RSS image availability)

## Alternative: Not Using AI Generation

**This is NOT supported.** The application is designed to require AI image generation.

If you absolutely cannot use OpenAI:
- You would need to modify the codebase significantly
- Remove AI generation requirement
- Implement alternative image source
- This is outside the scope of this documentation