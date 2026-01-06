"use client";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

export default function Navbar() {
  const { token, logout } = useAuth();

  return (
    <nav className="p-4 flex gap-4 bg-gray-800 text-white">
      <Link href="/">Home</Link>
      {token && (
        <>
          <Link href="/ingredients">Ingredients</Link>
          <Link href="/recipes">Recipes</Link>
          <Link href="/diary">Diary</Link>
          <button onClick={logout}>Logout</button>
        </>
      )}
      {!token && <Link href="/login">Login</Link>}
    </nav>
  );
}
