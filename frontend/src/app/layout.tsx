import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import Navbar from "@/components/Navbar";
import { AuthProvider } from "@/lib/auth";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Lottery System - Win Big with Secure Gaming",
  description: "Experience the thrill of winning with our secure and fair lottery platform. Buy tickets, participate in draws, and win amazing prizes!",
  keywords: "lottery, gaming, prizes, secure, fair, tickets, draws",
  authors: [{ name: "Lottery System" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${inter.className} antialiased`}>
        <AuthProvider>
          <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(to bottom right, #f8fafc, #dbeafe, #dcfce7)'
          }}>
            <div className="relative">
              {/* Background decoration */}
              <div style={{
                position: 'absolute',
                inset: 0,
                overflow: 'hidden',
                pointerEvents: 'none'
              }}>
                <div style={{
                  position: 'absolute',
                  top: '-160px',
                  right: '-160px',
                  width: '320px',
                  height: '320px',
                  backgroundColor: '#bbf7d0',
                  borderRadius: '50%',
                  mixBlendMode: 'multiply',
                  filter: 'blur(40px)',
                  opacity: 0.7,
                  animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
                }}></div>
                <div style={{
                  position: 'absolute',
                  bottom: '-160px',
                  left: '-160px',
                  width: '320px',
                  height: '320px',
                  backgroundColor: '#bfdbfe',
                  borderRadius: '50%',
                  mixBlendMode: 'multiply',
                  filter: 'blur(40px)',
                  opacity: 0.7,
                  animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                  animationDelay: '2s'
                }}></div>
                <div style={{
                  position: 'absolute',
                  top: '160px',
                  left: '160px',
                  width: '320px',
                  height: '320px',
                  backgroundColor: '#ddd6fe',
                  borderRadius: '50%',
                  mixBlendMode: 'multiply',
                  filter: 'blur(40px)',
                  opacity: 0.7,
                  animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                  animationDelay: '4s'
                }}></div>
              </div>

              <Navbar />
              <main style={{
                position: 'relative',
                zIndex: 10,
                maxWidth: '1280px',
                margin: '0 auto',
                padding: '32px 16px'
              }}>
                {children}
              </main>
            </div>
          </div>

          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                color: '#1f2937',
                borderRadius: '12px',
                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#22c55e',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </AuthProvider>
      </body>
    </html>
  );
}
