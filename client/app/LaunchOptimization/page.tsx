"use client";
import { useState } from "react";
import { title, subtitle } from "@/components/primitives";
import { Textarea, Button, Input, Select, SelectItem, Card, CardBody, Divider } from "@nextui-org/react";
import { getGeminiResponse, generateLaunchOptimizationPrompt } from "@/utils/geminiApi";

export default function LaunchOptimizationPage() {
  const [productDescription, setProductDescription] = useState("");
  const [competitorPricing, setCompetitorPricing] = useState("");
  const [ageGroup, setAgeGroup] = useState("");
  const [location, setLocation] = useState("");
  const [interests, setInterests] = useState("");
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const ageGroups = [
    { value: "18-24", label: "18-24" },
    { value: "25-34", label: "25-34" },
    { value: "35-44", label: "35-44" },
    { value: "45-54", label: "45-54" },
    { value: "55+", label: "55+" },
  ];

  const locations = [
    { value: "North America", label: "North America" },
    { value: "Europe", label: "Europe" },
    { value: "Asia", label: "Asia" },
    { value: "South America", label: "South America" },
    { value: "Africa", label: "Africa" },
    { value: "Australia/Oceania", label: "Australia/Oceania" },
  ];

  const interestOptions = [
    { value: "Technology", label: "Technology" },
    { value: "Fashion", label: "Fashion" },
    { value: "Health & Fitness", label: "Health & Fitness" },
    { value: "Food & Cooking", label: "Food & Cooking" },
    { value: "Travel", label: "Travel" },
    { value: "Finance", label: "Finance" },
    { value: "Education", label: "Education" },
  ];

  const handleOptimization = async () => {
    if (!productDescription) {
      alert("Product description is required");
      return;
    }

    console.log("Starting optimization process...");
    setIsLoading(true);
    setError("");
    setResult(null);

    try {
      // Create a fallback result in case API fails
      const fallbackResult = {
        product_name: `Optimized ${productDescription.split(' ')[0]}`,
        suggested_price: competitorPricing ? `Similar to competitors: ${competitorPricing}` : "Pricing depends on your market research",
        suggested_caption: `Perfect for ${ageGroup || 'all ages'} in ${location || 'any location'} interested in ${interests || 'your product'}.`
      };
      
      // Generate the prompt for Gemini API
      console.log("Generating prompt with inputs:", { 
        productDescription, 
        competitorPricing, 
        targetAudience: { age: ageGroup, location, interests } 
      });
      
      const prompt = generateLaunchOptimizationPrompt(
        productDescription,
        competitorPricing,
        {
          age: ageGroup,
          location: location,
          interests: interests,
        }
      );
      
      console.log("Generated prompt:", prompt);
      console.log("Sending request to Gemini API...");

      // Set timeout for API call to prevent hanging
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error("API request timeout after 10 seconds")), 10000)
      );
      
      try {
        // Call Gemini API with timeout
        const geminiResponse = await Promise.race([
          getGeminiResponse(prompt),
          timeoutPromise
        ]);

        console.log("Received raw Gemini response:", geminiResponse);
      
        // Parse the JSON response from Gemini
        let parsedResponse;
        try {
          console.log("Attempting to parse JSON response...");
          // Better JSON extraction from potential text response
          let jsonString = geminiResponse;
          
          // Extract JSON if wrapped in code blocks (markdown or otherwise)
          if (geminiResponse.includes("```")) {
            console.log("Found code blocks in response, extracting JSON...");
            const matches = geminiResponse.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
            if (matches && matches[1]) {
              jsonString = matches[1].trim();
              console.log("Extracted JSON from code block:", jsonString);
            } else {
              console.log("Failed to extract JSON from code blocks");
            }
          }
          
          console.log("Parsing JSON string:", jsonString);
          parsedResponse = JSON.parse(jsonString);
          console.log("Successfully parsed JSON:", parsedResponse);
        } catch (parseError) {
          console.error("Error parsing Gemini response:", parseError);
          console.log("Full response that failed to parse:", geminiResponse);
          // If parsing fails, use the raw text with fallback values
          parsedResponse = {
            product_name: "Could not generate product name from API response",
            suggested_price: "Could not generate price from API response",
            suggested_caption: geminiResponse || "Could not generate caption from API response",
          };
          console.log("Using fallback values:", parsedResponse);
        }

        console.log("Setting final result:", parsedResponse);
        setResult(parsedResponse);
      } catch (apiError) {
        console.error("API call failed, using fallback:", apiError);
        console.log("Using fallback data:", fallbackResult);
        setResult(fallbackResult);
        setError(`API request failed (using fallback data). Error: ${apiError.message}`);
        return; // Return early with fallback data
      }
    } catch (error) {
      console.error("Error in optimization flow:", error);
      console.error("Error details:", {
        message: error.message,
        stack: error.stack,
      });
      setError(`Failed to optimize product launch: ${error.message}. Please try again.`);
    } finally {
      console.log("Optimization process complete");
      setIsLoading(false);
    }
  };

  return (
    <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
      <div className="inline-block max-w-3xl text-center justify-center">
        <h1 className={title({ color: "blue" })}>Product Launch Optimization</h1>
        <br />
        <div className={subtitle({ class: "mt-4" })}>
          Enter your product details below to get AI-powered launch suggestions
        </div>
      </div>

      <div className="flex flex-col gap-5 w-full max-w-4xl">
        <Card className="p-4">
          <CardBody className="gap-5">
            <Textarea
              label="Product Description"
              placeholder="Enter a detailed description of your product"
              value={productDescription}
              onChange={(e) => setProductDescription(e.target.value)}
              required
              minRows={4}
            />

            <Input
              label="Competitor's Pricing (Optional)"
              placeholder="e.g., $99.99, €50-100"
              value={competitorPricing}
              onChange={(e) => setCompetitorPricing(e.target.value)}
            />

            <div className="text-lg font-medium mb-2">Target Audience</div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Select
                label="Age Group"
                placeholder="Select age group"
                selectedKeys={ageGroup ? [ageGroup] : []}
                onChange={(e) => setAgeGroup(e.target.value)}
              >
                {ageGroups.map((age) => (
                  <SelectItem key={age.value} value={age.value}>
                    {age.label}
                  </SelectItem>
                ))}
              </Select>

              <Select
                label="Location"
                placeholder="Select location"
                selectedKeys={location ? [location] : []}
                onChange={(e) => setLocation(e.target.value)}
              >
                {locations.map((loc) => (
                  <SelectItem key={loc.value} value={loc.value}>
                    {loc.label}
                  </SelectItem>
                ))}
              </Select>

              <Select
                label="Primary Interest"
                placeholder="Select primary interest"
                selectedKeys={interests ? [interests] : []}
                onChange={(e) => setInterests(e.target.value)}
              >
                {interestOptions.map((interest) => (
                  <SelectItem key={interest.value} value={interest.value}>
                    {interest.label}
                  </SelectItem>
                ))}
              </Select>
            </div>

            {error && (
              <div className="text-red-500 p-3 rounded-lg bg-red-50 text-center">
                {error}
              </div>
            )}

            {/* Change onClick to onPress for NextUI Button */}
            <Button
              color="primary"
              onPress={handleOptimization}
              isLoading={isLoading}
              className="mt-4"
            >
              {isLoading ? "Generating Suggestions..." : "Optimize Launch"}
            </Button>
          </CardBody>
        </Card>

        {result && (
          <Card className="mt-6">
            <CardBody className="gap-4">
              <h2 className="text-3xl font-semibold text-blue-600 text-center">
                AI-Generated Launch Suggestions
              </h2>
              
              <Divider className="my-2" />
              
              <div className="flex flex-col gap-4 mt-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="text-xl font-bold text-blue-700 mb-2">Suggested Product Name</h3>
                  <p className="text-lg">{result.product_name}</p>
                </div>
                
                <div className="p-4 bg-green-50 rounded-lg">
                  <h3 className="text-xl font-bold text-green-700 mb-2">Suggested Price</h3>
                  <p className="text-lg">{result.suggested_price}</p>
                </div>
                
                <div className="p-4 bg-purple-50 rounded-lg">
                  <h3 className="text-xl font-bold text-purple-700 mb-2">Suggested Caption</h3>
                  <p className="text-lg">{result.suggested_caption}</p>
                </div>
              </div>
            </CardBody>
          </Card>
        )}
      </div>
    </section>
  );
}
