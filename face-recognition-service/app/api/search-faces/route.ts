import { NextResponse } from "next/server"
import { createServerClient } from "@supabase/ssr"
import { cookies } from "next/headers"

export async function POST(request: Request) {
  try {
    const { referenceImageUrl, threshold = 0.6, eventId } = await request.json()

    const cookieStore = await cookies()
    const supabase = createServerClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!, {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value
        },
      },
    })

    const pythonApiUrl = process.env.PYTHON_API_URL || "http://localhost:8000"

    // Extract embedding from reference image
    const embeddingResponse = await fetch(`${pythonApiUrl}/api/extract-embeddings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_url: referenceImageUrl }),
    })

    if (!embeddingResponse.ok) {
      throw new Error("Failed to extract face embedding from reference image")
    }

    const { embeddings } = await embeddingResponse.json()

    if (!embeddings || embeddings.length === 0) {
      return NextResponse.json({
        success: false,
        message: "No face detected in reference image",
        matches: [],
      })
    }

    const referenceEmbedding = embeddings[0].vector

    // Search for similar faces
    const searchResponse = await fetch(`${pythonApiUrl}/api/search-faces`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        reference_embedding: referenceEmbedding,
        threshold,
        event_id: eventId,
      }),
    })

    if (!searchResponse.ok) {
      throw new Error("Failed to search for matching faces")
    }

    const { matches } = await searchResponse.json()

    // Get photo details from database
    const photoIds = matches.map((m: any) => m.photo_id)
    const { data: photos } = await supabase.from("photos").select("*").in("id", photoIds)

    return NextResponse.json({
      success: true,
      matches: photos || [],
    })
  } catch (error) {
    console.error("Error searching faces:", error)
    return NextResponse.json({ error: "Failed to search faces" }, { status: 500 })
  }
}
