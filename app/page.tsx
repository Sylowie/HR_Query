import { redirect } from "next/navigation";
import { connection } from "next/server";

export default function Home() {
  redirect("/chatbot");
}
