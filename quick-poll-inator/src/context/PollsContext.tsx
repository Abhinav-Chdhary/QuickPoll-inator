// src/context/PollsContext.tsx
"use client";
import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
// Helpers
import { PollResponse } from "@/components/helpers/types/Poll";
import { API_URL, WS_URL } from "@/components/helpers/constants";

// Define the shape of our context
interface PollsContextState {
  polls: PollResponse[];
  isLoading: boolean;
  error: string | null;
}

// Create the context
const PollsContext = createContext<PollsContextState | undefined>(undefined);

// Define the props for our provider
interface PollsProviderProps {
  children: ReactNode;
}

export function PollsProvider({ children }: PollsProviderProps) {
  const [polls, setPolls] = useState<PollResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initial data fetch
  useEffect(() => {
    const fetchInitialPolls = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_URL}/polls/`);
        if (!res.ok) {
          throw new Error("Failed to fetch polls");
        }
        const data: PollResponse[] = await res.json();
        setPolls(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchInitialPolls();
  }, []);

  // WebSocket connection and message handling
  useEffect(() => {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      // console.log("WebSocket message:", JSON.stringify(message));

      // A new poll was created
      if (message.type === "poll_created") {
        const newPoll = message.data as PollResponse;
        setPolls((prevPolls) => [newPoll, ...prevPolls]);
      }

      // An existing poll was updated (vote, like, new option)
      if (message.type === "poll_updated") {
        const updatedPoll = message.data as PollResponse;
        setPolls((prevPolls) =>
          prevPolls.map((p) => (p._id === updatedPoll._id ? updatedPoll : p))
        );
      }
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    // Cleanup on component unmount
    return () => {
      ws.close();
    };
  }, []); // Empty dependency array ensures this runs once

  const value = { polls, isLoading, error };

  return (
    <PollsContext.Provider value={value}>{children}</PollsContext.Provider>
  );
}

// Custom hook to easily consume the context
export function usePolls() {
  const context = useContext(PollsContext);
  if (context === undefined) {
    throw new Error("usePolls must be used within a PollsProvider");
  }
  return context;
}
