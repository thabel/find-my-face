"use client"

import type React from "react"

import { useState } from "react"
import { ArrowLeft, Upload, Plus } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { createBrowserClient } from "@supabase/ssr"

export default function ProducerPage() {
  const [step, setStep] = useState<"select" | "create" | "upload">("select")
  const [eventName, setEventName] = useState("")
  const [eventDescription, setEventDescription] = useState("")
  const [eventDate, setEventDate] = useState("")
  const [producerName, setProducerName] = useState("")
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  )

  const handleCreateEvent = async () => {
    if (!eventName || !eventDate || !producerName) {
      alert("Veuillez remplir tous les champs obligatoires")
      return
    }

    try {
      const { data, error } = await supabase
        .from("events")
        .insert({
          name: eventName,
          description: eventDescription,
          event_date: eventDate,
          created_by: producerName,
        })
        .select()
        .single()

      if (error) throw error

      setSelectedEvent(data.id)
      setStep("upload")
    } catch (error) {
      console.error("Error creating event:", error)
      alert("Erreur lors de la création de l'événement")
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0 || !selectedEvent) return

    setUploading(true)
    setUploadProgress(0)

    try {
      const totalFiles = files.length
      let uploadedCount = 0

      for (const file of Array.from(files)) {
        // Upload to Supabase Storage
        const fileName = `${selectedEvent}/${Date.now()}-${file.name}`
        const { error: uploadError } = await supabase.storage.from("event-photos").upload(fileName, file)

        if (uploadError) throw uploadError

        // Get public URL
        const { data: urlData } = supabase.storage.from("event-photos").getPublicUrl(fileName)

        // Save to database
        const { error: dbError } = await supabase.from("photos").insert({
          event_id: selectedEvent,
          file_path: urlData.publicUrl,
          file_name: file.name,
          uploaded_by: producerName,
        })

        if (dbError) throw dbError

        uploadedCount++
        setUploadProgress(Math.round((uploadedCount / totalFiles) * 100))
      }

      alert(`${uploadedCount} photos uploadées avec succès !`)
      setUploadProgress(0)
    } catch (error) {
      console.error("Error uploading files:", error)
      alert("Erreur lors de l'upload des photos")
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      <header className="border-b bg-background/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <Link href="/" className="inline-flex items-center gap-2 text-sm hover:text-primary transition-colors">
            <ArrowLeft className="h-4 w-4" />
            Retour à l'accueil
          </Link>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2">Espace Producer</h1>
            <p className="text-muted-foreground">Créez un événement et uploadez vos photos</p>
          </div>

          {step === "select" && (
            <Card className="p-8">
              <h2 className="text-2xl font-bold mb-6">Commencer</h2>
              <div className="space-y-4">
                <Button size="lg" className="w-full justify-start" onClick={() => setStep("create")}>
                  <Plus className="h-5 w-5 mr-2" />
                  Créer un nouvel événement
                </Button>
              </div>
            </Card>
          )}

          {step === "create" && (
            <Card className="p-8">
              <h2 className="text-2xl font-bold mb-6">Créer un événement</h2>
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="producer-name">Votre nom *</Label>
                  <Input
                    id="producer-name"
                    placeholder="Ex: Studio Photo Pro"
                    value={producerName}
                    onChange={(e) => setProducerName(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="event-name">Nom de l'événement *</Label>
                  <Input
                    id="event-name"
                    placeholder="Ex: Mariage de Sophie et Thomas"
                    value={eventName}
                    onChange={(e) => setEventName(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="event-date">Date de l'événement *</Label>
                  <Input id="event-date" type="date" value={eventDate} onChange={(e) => setEventDate(e.target.value)} />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="event-description">Description (optionnel)</Label>
                  <Textarea
                    id="event-description"
                    placeholder="Décrivez l'événement..."
                    value={eventDescription}
                    onChange={(e) => setEventDescription(e.target.value)}
                    rows={4}
                  />
                </div>

                <div className="flex gap-3">
                  <Button variant="outline" onClick={() => setStep("select")} className="flex-1">
                    Annuler
                  </Button>
                  <Button onClick={handleCreateEvent} className="flex-1">
                    Créer et continuer
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {step === "upload" && (
            <Card className="p-8">
              <h2 className="text-2xl font-bold mb-2">Upload des photos</h2>
              <p className="text-muted-foreground mb-6">
                Événement: <span className="font-semibold">{eventName}</span>
              </p>

              <div className="space-y-6">
                <div className="border-2 border-dashed rounded-lg p-12 text-center hover:border-primary transition-colors">
                  <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <h3 className="font-semibold mb-2">Sélectionnez vos photos</h3>
                  <p className="text-sm text-muted-foreground mb-4">Formats acceptés: JPG, PNG</p>
                  <Input
                    type="file"
                    multiple
                    accept="image/jpeg,image/png,image/jpg"
                    onChange={handleFileUpload}
                    disabled={uploading}
                    className="max-w-xs mx-auto"
                  />
                </div>

                {uploading && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Upload en cours...</span>
                      <span>{uploadProgress}%</span>
                    </div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  </div>
                )}

                <Button
                  variant="outline"
                  onClick={() => {
                    setStep("select")
                    setEventName("")
                    setEventDescription("")
                    setEventDate("")
                    setSelectedEvent(null)
                  }}
                  className="w-full"
                >
                  Terminer et créer un autre événement
                </Button>
              </div>
            </Card>
          )}
        </div>
      </main>
    </div>
  )
}
