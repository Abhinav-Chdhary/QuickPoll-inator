// src/components/ui/02_molecules/pollCard.tsx
import Link from "next/link";
import { Heart } from "lucide-react";
// Helpers
import { PollResponse } from "@/components/helpers/types/Poll";
// Components
import { Card, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

export default function PollCard({ poll }: { poll: PollResponse }) {
  return (
    <Link href={`/poll/${poll._id}`} passHref>
      {/* Card */}
      <Card className="shadow-md hover:shadow-lg hover:bg-muted/50 transition-all duration-200 cursor-pointer">
        {/* Header */}
        <CardHeader>
          {/* Title */}
          <CardTitle className="text-lg font-semibold">{poll.text}</CardTitle>
        </CardHeader>

        {/* Footer */}
        <CardFooter className="flex justify-between text-sm text-muted-foreground">
          {/* Likes */}
          <span className="flex items-center gap-1.5">
            {/* Icon */}
            <Heart className="h-4 w-4" />
            {/* Text */}
            {poll.likes} {poll.likes === 1 ? "Like" : "Likes"}
          </span>

          {/* Creation Date */}
          <span>
            Created on {new Date(poll.created_at).toLocaleDateString()}
          </span>
        </CardFooter>
      </Card>
    </Link>
  );
}
