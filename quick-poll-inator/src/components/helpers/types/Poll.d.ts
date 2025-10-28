// Poll option types
export interface PollOption {
  _id: string;
  poll_id: string;
  text: string;
  votes: number;
  created_at: string; // ISO date string
}

// Poll response types
export interface PollResponse {
  _id: string;
  text: string;
  likes: number;
  creator_id: string;
  created_at: string; // ISO date string
  options: PollOption[]; // This will be empty based on your GET /polls/ route
}
