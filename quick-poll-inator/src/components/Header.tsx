// src/components/Header.tsx
import Link from "next/link";

/**
 * A simple header component that displays the site title.
 */
export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/20">
      <div className="container flex h-14 max-w-screen-2xl items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2 px-4">
            {/* SVG logo here */}
            <span className="font-bold sm:inline-block text-xl">Quick Poll-inator</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
