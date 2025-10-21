import { NextResponse } from "next/server"
import { createServerClient } from "@supabase/ssr"
import { cookies } from "next/headers"

export async function POST(request: Request) {
  try {
    const { eventId } = await request.json()

    const cookieStore = await cookies()
    const supabase = createServerClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!, {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value
        },
      },
    })

    // Get unprocessed photos for this event
    const { data: photos, error } = await supabase
      .from("photos")
      .select("*")
      .eq("event_id", eventId)
      .eq("processed", false)

    if (error) throw error

    const pythonApiUrl = process.env.PYTHON_API_URL || "http://localhost:8000"

    for (const photo of photos || []) {
      try {
        // Call Python API to extract face embeddings
        const response = await fetch(`${pythonApiUrl}/api/extract-embeddings`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image_url: photo.file_path }),
        })

        if (!response.ok) continue

        const { embeddings } = await response.json()

        // Store embeddings in database
        for (const embedding of embeddings) {
          await supabase.from("face_embeddings").insert({
            photo_id: photo.id,
            embedding: embedding.vector,
            confidence: embedding.confidence,
          })
        }

        // Mark photo as processed
        await supabase.from("photos").update({ processed: true }).eq("id", photo.id)
      } catch (err) {
        console.error(`Error processing photo ${photo.id}:`, err)
      }
    }

    return NextResponse.json({
      success: true,
      photosProcessed: photos?.length || 0,
      message: "Photo processing completed",
    })
  } catch (error) {
    console.error("Error processing photos:", error)
    return NextResponse.json({ error: "Failed to process photos" }, { status: 500 })
  }
}
