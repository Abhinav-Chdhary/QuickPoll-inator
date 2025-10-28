import * as z from "zod";

// Zod schema for login (matches backend UserLogin)
export const loginSchema = z.object({
  email_id: z.string().email({
    message: "Please enter a valid email address.",
  }),
  password: z.string().min(1, {
    message: "Password is required.",
  }),
});

// Zod schema for registration (matches backend UserCreate)
export const registerSchema = z.object({
  name: z.string().min(2, {
    message: "Name must be at least 2 characters.",
  }),
  email_id: z.string().email({
    message: "Please enter a valid email address.",
  }),
  password: z.string().min(8, {
    message: "Password must be at least 8 characters.",
  }),
});

// Zod schema for poll creation validation
export const pollFormSchema = z.object({
  pollText: z.string().min(3, {
    message: "Poll question must be at least 3 characters.",
  }).max(300, {
    message: "Poll question must not exceed 300 characters.",
  }),
  options: z.array(
    z.object({
      text: z.string().min(1, {
        message: "Option text cannot be empty.",
      }).max(100, {
        message: "Option text must not exceed 100 characters.",
      }),
    })
  ).min(2, {
    message: "You must provide at least 2 options.",
  }),
});
