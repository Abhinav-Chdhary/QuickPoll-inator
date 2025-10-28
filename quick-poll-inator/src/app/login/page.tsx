// src/app/login/page.tsx
"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";
// Helpers
import { loginSchema, registerSchema } from "@/components/helpers/zodSchemas";
import { API_URL } from "@/components/helpers/constants";
// Components
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

export default function AuthPage() {
  const router = useRouter();

  // States for login
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // State to control the active tab
  const [activeTab, setActiveTab] = useState("login");

  // Effect to navigate user to home page if logged in
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      router.replace("/");
    }
  }, [router]);

  // Login Form
  const loginForm = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email_id: "",
      password: "",
    },
  });

  // Register Form
  const registerForm = useForm<z.infer<typeof registerSchema>>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      email_id: "",
      password: "",
    },
  });

  // Handlers

  /**
   * Handles the successful authentication
   * Stores token and redirects to the dashboard
   */
  const handleAuthSuccess = (data: { access_token: string; user: any }) => {
    // In a real app, you'd store this token securely (e.g., httpOnly cookie or context)
    localStorage.setItem("access_token", data.access_token);
    console.log("Authenticated user:", data.user);
    // Redirect to a home page
    router.push("/");
  };

  /**
   * Login form submission handler
   */
  async function onLoginSubmit(values: z.infer<typeof loginSchema>) {
    setIsLoading(true);
    setApiError(null);
    try {
      const res = await fetch(`${API_URL}/user/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });

      const data = await res.json();
      if (!res.ok) {
        if (res.status === 404) {
          // Set API error
          setApiError(data.detail || "User not found. Please register.");

          // Prefill the register form with the login email
          registerForm.setValue("email_id", values.email_id);
          setActiveTab("register");
        } else {
          setApiError(data.detail || "Login failed. Please try again.");
        }
        throw new Error(data.detail);
      }

      handleAuthSuccess(data);
    } catch (error: any) {
      if (!apiError) {
        setApiError(error.message);
      }
    } finally {
      setIsLoading(false);
    }
  }

  /**
   * Register form submission handler
   */
  async function onRegisterSubmit(values: z.infer<typeof registerSchema>) {
    setIsLoading(true);
    setApiError(null);
    try {
      const res = await fetch(`${API_URL}/user/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(
          data.detail || "Registration failed. Please try again."
        );
      }

      // Automatically log the user in after successful registration
      handleAuthSuccess(data);
    } catch (error: any) {
      setApiError(error.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-background p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        {/* Tabs */}
        <Tabs
          defaultValue={activeTab}
          onValueChange={(value) => {
            setActiveTab(value);
            setApiError(null);
          }}
          className="w-[400px]"
        >
          {/* Card */}
          <Card className="shadow-lg">
            {/* Card Header */}
            <CardHeader>
              {/* Tabs List */}
              <TabsList className="grid w-full grid-cols-2">
                {/* Login Tab header */}
                <TabsTrigger value="login" onClick={() => setApiError(null)}>
                  Login
                </TabsTrigger>

                {/* Register Tab header */}
                <TabsTrigger value="register" onClick={() => setApiError(null)}>
                  Register
                </TabsTrigger>
              </TabsList>
            </CardHeader>

            {/* Login Tab */}
            <TabsContent value="login">
              <CardContent className="space-y-4">
                <Form {...loginForm}>
                  <form
                    onSubmit={loginForm.handleSubmit(onLoginSubmit)}
                    className="space-y-4"
                  >
                    {/* Email field */}
                    <FormField
                      control={loginForm.control}
                      name="email_id"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Email</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="user@example.com"
                              {...field}
                              disabled={isLoading}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Password field */}
                    <FormField
                      control={loginForm.control}
                      name="password"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Password</FormLabel>
                          <FormControl>
                            <Input
                              type="password"
                              placeholder="••••••••"
                              {...field}
                              disabled={isLoading}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Error message */}
                    {apiError && (
                      <p className="text-sm text-destructive">{apiError}</p>
                    )}

                    {/* Submit button */}
                    <Button
                      type="submit"
                      className="w-full"
                      disabled={isLoading}
                    >
                      {isLoading && (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      )}
                      {isLoading ? "Signing in..." : "Login"}
                    </Button>
                  </form>
                </Form>
              </CardContent>
            </TabsContent>

            {/* Register Tab */}
            <TabsContent value="register">
              <CardContent className="space-y-4">
                <Form {...registerForm}>
                  <form
                    onSubmit={registerForm.handleSubmit(onRegisterSubmit)}
                    className="space-y-4"
                  >
                    {/* Name field */}
                    <FormField
                      control={registerForm.control}
                      name="name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Full Name</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Your Name"
                              {...field}
                              disabled={isLoading}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Email field */}
                    <FormField
                      control={registerForm.control}
                      name="email_id"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Email</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="user@example.com"
                              {...field}
                              disabled={isLoading}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Password field */}
                    <FormField
                      control={registerForm.control}
                      name="password"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Password</FormLabel>
                          <FormControl>
                            <Input
                              type="password"
                              placeholder="Minimum 8 characters"
                              {...field}
                              disabled={isLoading}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Error message */}
                    {apiError && (
                      <p className="text-sm text-destructive">{apiError}</p>
                    )}

                    {/* Submit button */}
                    <Button
                      type="submit"
                      className="w-full"
                      disabled={isLoading}
                    >
                      {isLoading && (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      )}
                      {isLoading ? "Creating account..." : "Create Account"}
                    </Button>
                  </form>
                </Form>
              </CardContent>
            </TabsContent>
          </Card>
        </Tabs>
      </motion.div>
    </div>
  );
}
