import Link from "next/link";

export default function HomePage() {
  return (
    <section className="flex flex-col items-start gap-6">
      <h1 className="text-4xl font-bold leading-tight">
        Smart Nutrition,
        <span className="text-brand"> Simplified</span>
      </h1>

      <p className="max-w-2xl text-gray-600 text-lg">
        Nutri-App helps you manage your pantry and generate diet plans based on
        available ingredients and nutrition data.
      </p>

      <div className="flex gap-4">
        <Link
          href="/pantry"
          className="rounded-md bg-brand px-6 py-3 text-white font-medium hover:bg-brand-dark"
        >
          View Pantry
        </Link>

        <Link
          href="/diet"
          className="rounded-md border border-gray-300 px-6 py-3 font-medium hover:bg-gray-100"
        >
          Generate Diet
        </Link>
      </div>
    </section>
  );
}
