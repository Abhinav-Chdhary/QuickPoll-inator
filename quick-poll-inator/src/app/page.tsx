// src/app/page.tsx
"use client";
import { motion } from "framer-motion";
import { Loader2, Plus } from "lucide-react";
import Link from "next/link";
// Helpers
import { usePolls } from "@/context/PollsContext";
// Components
import ProtectedRoute from "@/components/ProtectedRoutes";
import PollCard from "@/components/ui/02_molecules/pollCard";
import { Button } from "@/components/ui/button";

export default function Home() {
  // Import from PollsContext
  const { polls, isLoading, error } = usePolls();

  // Render content based on state
  const renderContent = () => {
    // Loading state
    if (isLoading) {
      return (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <p className="ml-2">Loading polls...</p>
        </div>
      );
    }

    // Error state
    if (error) {
      return (
        <div className="text-center py-20 text-destructive">
          <p>Error: {error}</p>
          <p>Could not load polls. Please try again later.</p>
        </div>
      );
    }

    // No polls found state
    if (polls.length === 0) {
      return (
        <div className="text-center py-20 text-muted-foreground space-y-4">
          <p className="text-lg">No polls found.</p>
          <p>Why not be the first to create one?</p>
          <Button asChild>
            <Link href="/poll/create">
              <Plus className="h-4 w-4 mr-2" />
              Make your own
            </Link>
          </Button>
        </div>
      );
    }

    // Polls found state
    return (
      <div className="flex flex-col space-y-4">
        {polls.map((poll) => (
          <PollCard key={poll._id} poll={poll} />
        ))}
      </div>
    );
  };

  return (
    <ProtectedRoute>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="container mx-auto max-w-2xl py-10 px-4" // Centered layout
      >
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            {/* Title */}
            <h1 className="text-3xl font-bold tracking-tight">Home Feed</h1>

            {/* Description */}
            <p className="text-muted-foreground">
              See what the community is polling about.
            </p>
          </div>

          {/* Create Poll Button */}
          <Button asChild className="shrink-0">
            {/* Link */}
            <Link href="/poll/create">
              {/* Icon */}
              <Plus className="h-4 w-4 mr-2" />
              {/* Text */}
              Make your own
            </Link>
          </Button>
        </div>

        {renderContent()}
      </motion.div>
    </ProtectedRoute>
  );
}
