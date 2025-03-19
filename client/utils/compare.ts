import { NextApiRequest, NextApiResponse } from "next";
import Sentiment from "sentiment";

const sentiment = new Sentiment();

// API Keys (Avoid hardcoding in production)
const GEMINI_API_KEY = "AIzaSyD30Q3CDEjLT8nWoJYb63h3rOL18KK6QCc";
const SCRAPER_API_KEY = "29ad67281f2f050c70a218b301fd1164";

// Gemini API URL
const API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent";

// Function to fetch reviews from a given URL
export async function fetchReviews(url: string): Promise<string[]> {
  try {
    const response = await fetch(
      `https://api.scraperapi.com/?api_key=${SCRAPER_API_KEY}&url=${encodeURIComponent(url)}&autoparse=true`
    );
    const data = await response.json();
    return data.reviews?.map((review: { review: string }) => review.review) || [];
  } catch (error) {
    console.error("Error fetching reviews:", error);
    return [];
  }
}

// Function to analyze sentiment using Sentiment.js
export function analyzeSentiment(reviews: string[]): number {
  if (reviews.length === 0) return 0;

  return (
    reviews
      .map((review) => {
        const result = sentiment.analyze(review);
        return result.score || 0;
      })
      .reduce((a, b) => a + b, 0) / reviews.length
  );
}

// Function to call Gemini API
export async function getGeminiResponse(prompt: string): Promise<string> {
  try {
    console.log("getGeminiResponse - Starting API call");
    console.log(
      "Using API key (redacted):",
      GEMINI_API_KEY
        ? `${GEMINI_API_KEY.substring(0, 5)}...${GEMINI_API_KEY.substring(GEMINI_API_KEY.length - 4)}`
        : "undefined"
    );

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
      },
    };

    console.log("Request body:", JSON.stringify(requestBody, null, 2));

    const response = await fetch(`${API_URL}?key=${apiKey}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    const result = await response.json();
    return result?.candidates?.[0]?.content?.parts?.[0]?.text || "Summarization failed.";
  } catch (error) {
    console.error("Error summarizing with Gemini:", error);
    return "Summarization error.";
  }
}

// Function to summarize reviews using Gemini API
export async function summarizeReviewsGemini(reviews: string[], numSentences = 3): Promise<string> {
  if (!reviews.length) return "No reviews available.";

  const text = reviews.join(" ");
  const prompt = `Summarize the following customer reviews in ${numSentences} sentences:\n\n${text}`;

  return await getGeminiResponse(prompt);
}

// Function to generate a comparison reason using Gemini API
export async function generateComparisonReason(
  reviews1: string[],
  reviews2: string[],
  sentiment1: number,
  sentiment2: number
): Promise<string> {
  const text1 = reviews1.join(" ");
  const text2 = reviews2.join(" ");

  const prompt = `Compare the following two sets of customer reviews and explain why one product might be better than the other based on the reviews. Focus on key differences in customer feedback.

Product 1 Reviews:
${text1}

Product 2 Reviews:
${text2}

Sentiment Scores:
- Product 1: ${sentiment1.toFixed(2)}
- Product 2: ${sentiment2.toFixed(2)}

Provide a detailed comparison in 2-3 sentences.`;

  return await getGeminiResponse(prompt);
}

// API Route Handler
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { url1, url2 } = req.body;
  if (!url1 || !url2) {
    return res.status(400).json({ error: "Both URLs are required" });
  }

  try {
    // Fetch and process reviews for Product 1
    const reviews1 = await fetchReviews(url1);
    const summary1 = await summarizeReviewsGemini(reviews1);
    const sentiment1 = analyzeSentiment(reviews1);

    // Fetch and process reviews for Product 2
    const reviews2 = await fetchReviews(url2);
    const summary2 = await summarizeReviewsGemini(reviews2);
    const sentiment2 = analyzeSentiment(reviews2);

    // Generate a comparison reason
    const comparisonReason = await generateComparisonReason(reviews1, reviews2, sentiment1, sentiment2);

    // Determine the better product
    let bestProduct, explanation;
    if (sentiment1 > sentiment2) {
      bestProduct = "Product 1";
      explanation = `Product 1 has a better sentiment score (${sentiment1.toFixed(2)}) compared to Product 2 (${sentiment2.toFixed(2)}).`;
    } else if (sentiment2 > sentiment1) {
      bestProduct = "Product 2";
      explanation = `Product 2 has a better sentiment score (${sentiment2.toFixed(2)}) compared to Product 1 (${sentiment1.toFixed(2)}).`;
    } else {
      bestProduct = "Both products have similar sentiment.";
      explanation = "Both products have comparable sentiment ratings based on customer feedback.";
    }

    return res.status(200).json({
      product1: { sentiment: sentiment1.toFixed(2), summary: summary1 },
      product2: { sentiment: sentiment2.toFixed(2), summary: summary2 },
      bestProduct,
      explanation,
      comparisonReason, // Include the detailed comparison reason
    });
  } catch (error) {
    console.error("Error processing request:", error);
    return res.status(500).json({ error: "Internal server error" });
  }
}