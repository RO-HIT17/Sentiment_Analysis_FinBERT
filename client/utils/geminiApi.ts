// Explicitly use the environment variable without relying on process.env
const GEMINI_API_KEY = process.env.NEXT_PUBLIC_GEMINI_API_KEY ;
const API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent";

export async function getGeminiResponse(prompt: string) {
  try {
    console.log("getGeminiResponse - Starting API call");
    console.log("Using API key (redacted):", GEMINI_API_KEY ? `${GEMINI_API_KEY.substring(0, 5)}...${GEMINI_API_KEY.substring(GEMINI_API_KEY.length - 4)}` : "undefined");
    
    // Use a hardcoded API key as fallback if environment variable is not available
    const apiKey = GEMINI_API_KEY || "AIzaSyD30Q3CDEjLT8nWoJYb63h3rOL18KK6QCc";
    
    if (!apiKey) {
      console.error("API key is undefined or empty after fallback");
      throw new Error("Missing API key. Please check your .env.local file.");
    }
    
    const requestBody = {
      contents: [
        {
          parts: [
            {
              text: prompt,
            },
          ],
        },
      ],
      generationConfig: {
        temperature: 0.7,
        maxOutputTokens: 1024,
      }
    };
    
    console.log("Request body:", JSON.stringify(requestBody, null, 2));
    
    const response = await fetch(`${API_URL}?key=${apiKey}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    console.log("Response status:", response.status);
    console.log("Response status text:", response.statusText);
    console.log("Response headers:", Object.fromEntries([...response.headers.entries()]));

    if (!response.ok) {
      // Log more details about the error
      const errorText = await response.text();
      console.error(`API Error (${response.status}):`, errorText);
      throw new Error(`API request failed: ${response.status} - ${response.statusText} - ${errorText}`);
    }

    console.log("Response is OK, parsing JSON");
    const data = await response.json();
    console.log("Response data structure:", Object.keys(data));
    
    // Check for expected response format
    if (!data.candidates) {
      console.error("Missing 'candidates' in response:", data);
      throw new Error("Invalid response format: missing candidates");
    }
    
    if (!data.candidates[0]) {
      console.error("Empty candidates array:", data.candidates);
      throw new Error("Invalid response format: empty candidates array");
    }
    
    if (!data.candidates[0].content) {
      console.error("Missing 'content' in first candidate:", data.candidates[0]);
      throw new Error("Invalid response format: missing content in candidate");
    }
    
    if (!data.candidates[0].content.parts || data.candidates[0].content.parts.length === 0) {
      console.error("Missing 'parts' in content:", data.candidates[0].content);
      throw new Error("Invalid response format: missing parts in content");
    }
    
    const responseText = data.candidates[0].content.parts[0].text;
    console.log("Successfully extracted response text, length:", responseText.length);
    return responseText;
  } catch (error) {
    console.error("Error in getGeminiResponse:", error);
    console.error("Error type:", error.constructor.name);
    console.error("Error message:", error.message);
    console.error("Error stack:", error.stack);
    throw error;
  }
}

export function generateLaunchOptimizationPrompt(
  productDescription: string,
  competitorPricing: string,
  targetAudience: {
    age: string;
    location: string;
    interests: string;
  }
) {
  // Improved prompt with clearer instructions
  return `
You are a product marketing expert tasked with analyzing product information and providing launch recommendations.

PRODUCT DESCRIPTION:
${productDescription}

COMPETITOR'S PRICING:
${competitorPricing || "Not provided"}

TARGET AUDIENCE:
- Age Group: ${targetAudience.age || "Not specified"}
- Location: ${targetAudience.location || "Not specified"}
- Primary Interest: ${targetAudience.interests || "Not specified"}

Based on this information, please provide the following in valid JSON format only:
- Suggest 3-4 potential product names
- A suggested competitive price point with an explanation for why this price is appropriate
- A compelling marketing caption tailored to the target audience
- An explanation of why the marketing caption will emotionally resonate with customers and drive engagement

Return ONLY a JSON object with the following format:
{
  "product_names": [
    "First suggested product name",
    "Second suggested product name",
    "Third suggested product name",
    "Fourth suggested product name (optional)"
  ],
  "suggested_price": "Your suggested price",
  "price_explanation": "Your explanation for why this price point is appropriate",
  "suggested_caption": "Your suggested marketing caption",
  "caption_sentiment_explanation": "Explanation of how the caption's emotional tone and sentiment will attract the target audience"
}
`;
}
