"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";

export default function LoginPage() {
  // States
  const [step, setStep] = useState<"enter" | "otp">("enter");
  const [identifier, setIdentifier] = useState("");
  const [otp, setOtp] = useState("");
  const [generatedOtp, setGeneratedOtp] = useState<string | null>(null);

  // Send OTP
  const sendOtp = () => {
    if (!identifier) return alert("Please enter your email or phone number");
    const fakeOtp = Math.floor(100000 + Math.random() * 900000).toString();
    setGeneratedOtp(fakeOtp);
    console.log("Generated OTP:", fakeOtp); // for demo
    setStep("otp");
  };

  // Verify OTP
  const verifyOtp = () => {
    if (otp === generatedOtp) {
      alert("✅ Logged in successfully!");
      // navigate to dashboard or homepage
    } else {
      alert("❌ Invalid OTP, please try again.");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        {/* Card header */}
        <Card className="w-[360px] shadow-lg">
          <CardHeader>
            <CardTitle className="text-center text-2xl font-semibold">
              OTP Login
            </CardTitle>
          </CardHeader>

          {/* Login card */}
          <CardContent>
            {/* Step 1 : Enter your email or phone number */}
            {step === "enter" && (
              <div className="space-y-4">
                <Input
                  type="text"
                  placeholder="Enter email"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                />
                <Button className="w-full" onClick={sendOtp}>
                  Send OTP
                </Button>
              </div>
            )}

            {/* Step 2 : Enter OTP */}
            {step === "otp" && (
              <div className="space-y-4">
                <Input
                  type="text"
                  placeholder="Enter OTP"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                />
                <Button className="w-full" onClick={verifyOtp}>
                  Verify OTP
                </Button>
                <Button
                  variant="ghost"
                  className="w-full text-sm"
                  onClick={() => setStep("enter")}
                >
                  ← Change Email / Phone
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
