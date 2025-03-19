'use client';

import { useState } from "react";
import { title, subtitle } from "@/components/primitives";
import { Textarea, Button, Input, Select, SelectItem, Card, CardBody, Divider } from "@nextui-org/react";
import { fetchReviews, summarizeReviewsGemini, analyzeSentiment, generateComparisonReason } from "@/utils/compare";
import { Loader2 } from "lucide-react";

export default function CompareProductsPage() {
  const [url1, setUrl1] = useState('');
  const [url2, setUrl2] = useState('');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCompare = async () => {
    if (!url1 || !url2) {
      setError('Please enter both product URLs.');
      return;
    }
    setIsLoading(true);
    setError('');

    try {
      const reviews1 = await fetchReviews(url1);
      const summary1 = await summarizeReviewsGemini(reviews1);
      const sentiment1 = analyzeSentiment(reviews1);

      const reviews2 = await fetchReviews(url2);
      const summary2 = await summarizeReviewsGemini(reviews2);
      const sentiment2 = analyzeSentiment(reviews2);

      const comparisonReason = await generateComparisonReason(reviews1, reviews2, sentiment1, sentiment2);

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

      setResults({
        product1: { sentiment: sentiment1.toFixed(2), summary: summary1 },
        product2: { sentiment: sentiment2.toFixed(2), summary: summary2 },
        bestProduct,
        explanation,
        comparisonReason,
      });
    } catch (err) {
      setError('Failed to compare products. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
      <div className="inline-block max-w-3xl text-center justify-center">
        <h1 className={title({ color: "blue" })}>Compare Products</h1>
        <br />
        <div className={subtitle({ class: "mt-4" })}>
          Enter the URLs of two products to compare their reviews and sentiment.
        </div>
      </div>

      <div className="flex flex-col gap-5 w-full max-w-4xl">
        <Card className="p-4">
          <CardBody className="gap-5">
            <Input
              type="text"
              label="Product 1 URL"
              placeholder="Enter URL for Product 1"
              value={url1}
              onChange={(e) => setUrl1(e.target.value)}
              required
            />

            <Input
              type="text"
              label="Product 2 URL"
              placeholder="Enter URL for Product 2"
              value={url2}
              onChange={(e) => setUrl2(e.target.value)}
              required
            />

            {error && (
              <div className="text-red-500 p-3 rounded-lg bg-red-50 text-center">
                {error}
              </div>
            )}

            <Button
              color="primary"
              onPress={handleCompare}
              isLoading={isLoading}
              className="mt-4"
            >
              {isLoading ? "Comparing..." : "Compare Products"}
            </Button>
          </CardBody>
        </Card>

        {results && (
          <Card className="mt-6">
            <CardBody className="gap-4">
              <h2 className="text-3xl font-semibold text-blue-600 text-center">
                Comparison Results
              </h2>
              
              <Divider className="my-2" />
              
              <div className="flex flex-col gap-4 mt-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="text-xl font-bold text-blue-700 mb-2">Product 1</h3>
                  <p><strong>Sentiment Score:</strong> {results.product1.sentiment}</p>
                  <p><strong>Summary:</strong> {results.product1.summary}</p>
                </div>
                
                <div className="p-4 bg-green-50 rounded-lg">
                  <h3 className="text-xl font-bold text-green-700 mb-2">Product 2</h3>
                  <p><strong>Sentiment Score:</strong> {results.product2.sentiment}</p>
                  <p><strong>Summary:</strong> {results.product2.summary}</p>
                </div>
                
                <div className="p-4 bg-purple-50 rounded-lg">
                  <h3 className="text-xl font-bold text-purple-700 mb-2">Conclusion</h3>
                  <p><strong>Best Product:</strong> {results.bestProduct}</p>
                  <p>{results.explanation}</p>
                </div>

                <div className="p-4 bg-orange-50 rounded-lg">
                  <h3 className="text-xl font-bold text-orange-700 mb-2">Why its better?</h3>
                  <p>{results.comparisonReason}</p>
                </div>
              </div>
            </CardBody>
          </Card>
        )}
      </div>
    </section>
  );
}