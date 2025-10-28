// src/app/poll/[poll_id]/page.tsx
"use client";
import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Heart, Loader2, Check } from "lucide-react";
import { cn } from "@/lib/utils";
// Helpers
import { API_URL } from "@/components/helpers/constants";
import { usePolls } from "@/context/PollsContext";
// Components
import ProtectedRoute from "@/components/ProtectedRoutes";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PollResponse } from "@/components/helpers/types/Poll";

export default function PollDetailPage() {
  const params = useParams();
  const router = useRouter();

  // Get poll_id from URL
  const poll_id = params.poll_id as string;

  // Poll related states
  const [poll, setPoll] = useState<PollResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOptionId, setSelectedOptionId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Get polls list from context
  const { polls: globalPolls } = usePolls();

  // Data Fetching
  const fetchPoll = async () => {
    if (!poll_id) return;

    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/polls/${poll_id}`);
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to fetch poll");
      }
      const data: PollResponse = await res.json();
      setPoll(data);
    } catch (error: any) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch poll on mount
  useEffect(() => {
    fetchPoll();
  }, [poll_id]);

  // Effect to sync local state with context
  useEffect(() => {
    // Find poll in the global list
    const updatedPollFromContext = globalPolls.find((p) => p._id === poll_id);

    // If poll is found, update local state
    if (updatedPollFromContext) {
      setPoll(updatedPollFromContext);
    }
  }, [globalPolls, poll_id]);

  // Event Handlers
  const handleVote = async (optionId: string) => {
    // This calls POST /{poll_id}/options/{option_id}/vote
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login"); // Redirect if not logged in
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await fetch(
        `${API_URL}/polls/${poll_id}/options/${optionId}/vote`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to cast vote");
      }

      // Set the selected option in the UI
      setSelectedOptionId(optionId);
    } catch (error: any) {
      setError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Like a poll
  const handleLike = async () => {
    // This calls POST /{poll_id}/like
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_URL}/polls/${poll_id}/like`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to update like");
      }
    } catch (error: any) {
      setError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Render Logic
  // Loading
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="ml-2">Loading Poll...</p>
      </div>
    );
  }

  // Error
  if (error) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen text-destructive">
        <p className="text-lg font-semibold">Error</p>
        <p>{error}</p>
        <Button variant="outline" onClick={fetchPoll} className="mt-4">
          Try Again
        </Button>
      </div>
    );
  }

  // Poll not found
  if (!poll) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <p>Poll not found.</p>
      </div>
    );
  }

  // Calculate total votes
  const totalVotes = poll.options.reduce(
    (acc, option) => acc + option.votes,
    0
  );

  return (
    <ProtectedRoute>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="container mx-auto max-w-2xl py-10 px-4"
      >
        {/* Poll Card */}
        <Card>
          {/* Header */}
          <CardHeader>
            {/* Title */}
            <CardTitle className="text-2xl font-bold">{poll.text}</CardTitle>
            {/* Creation Date */}
            <p className="text-sm text-muted-foreground">
              Created on {new Date(poll.created_at).toLocaleDateString()}
            </p>
          </CardHeader>

          {/* Content */}
          <CardContent className="space-y-4">
            <h3 className="font-semibold">Options</h3>

            {/* Poll options */}
            <div className="space-y-3">
              {poll.options.map((option) => {
                const votePercentage =
                  totalVotes > 0 ? (option.votes / totalVotes) * 100 : 0;
                const isSelected = selectedOptionId === option._id;

                return (
                  <div key={option._id} className="space-y-2">
                    {/* Option */}
                    <div className="flex justify-between text-sm">
                      {/* Text */}
                      <span className="font-medium">{option.text}</span>

                      {/* Votes */}
                      <span className="text-muted-foreground">
                        {option.votes} {option.votes === 1 ? "vote" : "votes"}
                      </span>
                    </div>

                    {/* Vote Button */}
                    <Button
                      variant="outline"
                      className="w-full h-auto justify-start p-0 overflow-hidden"
                      onClick={() => handleVote(option._id)}
                      disabled={isSubmitting}
                    >
                      <div className="relative w-full h-10">
                        {/* Vote bar */}
                        <motion.div
                          className={cn(
                            "absolute top-0 left-0 h-full bg-primary/20"
                          )}
                          initial={{ width: 0 }}
                          animate={{ width: `${votePercentage}%` }}
                          transition={{ duration: 0.5 }}
                        />

                        {/* Vote and percentage */}
                        <span
                          className={cn(
                            "absolute inset-0 flex items-center px-4 font-medium"
                          )}
                        >
                          {/* Vote */}
                          {isSelected && <Check className="h-4 w-4 mr-2" />}
                          {/* Percentage */}
                          {votePercentage.toFixed(0)}%
                        </span>
                      </div>
                    </Button>
                  </div>
                );
              })}
            </div>
          </CardContent>

          {/* Footer */}
          <CardFooter className="flex justify-between">
            {/* Like Button */}
            <Button
              variant="outline"
              onClick={handleLike}
              disabled={isSubmitting}
            >
              {/* Icon */}
              <Heart className="h-4 w-4 mr-2" />
              {/* Text */}
              {poll.likes} {poll.likes === 1 ? "Like" : "Likes"}
            </Button>

            {/* Total votes */}
            <div className="text-sm text-muted-foreground">
              Total Votes: {totalVotes}
            </div>
          </CardFooter>
        </Card>
      </motion.div>
    </ProtectedRoute>
  );
}
