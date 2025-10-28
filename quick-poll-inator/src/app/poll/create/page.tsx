// src/app/poll/create/page.tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { motion } from "framer-motion";
import { Loader2, Plus, X } from "lucide-react";
// Helpers
import { API_URL } from "@/components/helpers/constants";
import { PollResponse } from "@/components/helpers/types/Poll";
import { pollFormSchema } from "@/components/helpers/zodSchemas";
// Components
import ProtectedRoute from "@/components/ProtectedRoutes";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Separator } from "@/components/ui/separator";

// Type for form values
type PollFormValues = z.infer<typeof pollFormSchema>;

export default function CreatePollPage() {
  const router = useRouter();

  // Loading states
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // Form instance
  const form = useForm<PollFormValues>({
    resolver: zodResolver(pollFormSchema),
    defaultValues: {
      pollText: "",
      options: [{ text: "" }, { text: "" }], // Start with 2 options
    },
  });

  // `useFieldArray` for dynamic option fields
  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "options",
  });

  // Form submission handler
  const onSubmit = async (values: PollFormValues) => {
    setIsLoading(true);
    setApiError(null);

    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    try {
      // Create the Poll
      const pollRes = await fetch(`${API_URL}/polls/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ text: values.pollText }),
      });

      const createdPoll: PollResponse = await pollRes.json();
      if (!pollRes.ok) {
        throw new Error(
          (createdPoll as any).detail || "Failed to create poll."
        );
      }

      // Add all options to the new poll
      const pollId = createdPoll._id;
      const optionPromises = values.options.map((option) => {
        return fetch(`${API_URL}/polls/${pollId}/options`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ text: option.text }),
        });
      });

      const optionResults = await Promise.all(optionPromises);

      // Check if any option failed to be added
      const failedOption = optionResults.find((res) => !res.ok);
      if (failedOption) {
        throw new Error("Poll created, but failed to add one or more options.");
      }

      // Success, navigate to the new poll
      setIsLoading(false);
      router.push(`/poll/${pollId}`);
    } catch (error: any) {
      setApiError(error.message);
      setIsLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="container mx-auto max-w-2xl py-10 px-4"
      >
        {/* Create poll form */}
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            {/* Poll form card */}
            <Card>
              <CardHeader>
                {/* Title */}
                <CardTitle>Create a New Poll</CardTitle>

                {/* Description */}
                <CardDescription>
                  Fill out your question and provide at least two options.
                </CardDescription>
              </CardHeader>

              {/* Poll form content */}
              <CardContent className="space-y-6">
                {/* Poll Question */}
                <FormField
                  control={form.control}
                  name="pollText"
                  render={({ field }) => (
                    <FormItem>
                      {/* Label */}
                      <FormLabel className="text-lg font-semibold">
                        Poll Question
                      </FormLabel>

                      {/* Input */}
                      <FormControl>
                        <Input
                          placeholder="What's your favorite color?"
                          {...field}
                          disabled={isLoading}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Separator />

                {/* Dynamic Options */}
                <div className="space-y-4">
                  {/* Label */}
                  <FormLabel className="text-lg font-semibold">
                    Options
                  </FormLabel>

                  {/* Options */}
                  {fields.map((field, index) => (
                    <FormField
                      key={field.id}
                      control={form.control}
                      name={`options.${index}.text`}
                      render={({ field }) => (
                        <FormItem>
                          <div className="flex items-center gap-2">
                            {/* Input */}
                            <FormControl>
                              <Input
                                placeholder={`Option ${index + 1}`}
                                {...field}
                                disabled={isLoading}
                              />
                            </FormControl>

                            {/* Remove button */}
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              onClick={() => remove(index)}
                              disabled={fields.length <= 2 || isLoading}
                              className={
                                fields.length <= 2
                                  ? "text-muted-foreground/50"
                                  : "text-destructive"
                              }
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>

                          {/* Message */}
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  ))}

                  {/* Add Option button */}
                  <Button
                    type="button"
                    variant="outline"
                    className="w-full"
                    onClick={() => append({ text: "" })}
                    disabled={isLoading}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Option
                  </Button>
                </div>
              </CardContent>

              {/* Footer */}
              <CardFooter className="flex flex-col items-start space-y-4">
                {/* Error message */}
                {apiError && (
                  <p className="text-sm text-destructive">{apiError}</p>
                )}

                {/* Submit button */}
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  {isLoading ? "Creating Poll..." : "Create Poll"}
                </Button>
              </CardFooter>
            </Card>
          </form>
        </Form>
      </motion.div>
    </ProtectedRoute>
  );
}
