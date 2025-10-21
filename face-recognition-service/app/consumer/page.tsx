"use client"

import type React from "react"

import { useState } from "react"
import { ArrowLeft, Upload, Search, Download } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import Image from "next/image"

export default function ConsumerPage() {
  const [step, setStep] = useState<"upload" | "results">("upload")
  const [referenceImage, setReferenceImage] = useState<string | null>(null)
  const [searching, setSearching] = useState(false)
  const [matchedPhotos, setMatchedPhotos] = useState<string[]>([])

  const handleReferenceUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      setReferenceImage(e.target?.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleSearch = async () => {
    if (!referenceImage) return

    setSearching(true)

    // TODO: Implement face recognition search
    // This would call your Python backend with InsightFace
    // For now, simulating a search
    setTimeout(() => {
      setMatchedPhotos(["/event-photo-person-smiling.jpg", "/event-photo-group-celebration.jpg", "/event-photo-portrait-happy.jpg"])
      setSearching(false)
      setStep("results")
    }, 2000)
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
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2">Espace Consumer</h1>
            <p className="text-muted-foreground">Trouvez vos photos grâce à la reconnaissance faciale</p>
          </div>

          {step === "upload" && (
            <Card className="p-8">
              <h2 className="text-2xl font-bold mb-6">Uploadez votre photo de référence</h2>

              <div className="space-y-6">
                <div className="border-2 border-dashed rounded-lg p-12 text-center hover:border-primary transition-colors">
                  {referenceImage ? (
                    <div className="space-y-4">
                      <div className="relative w-48 h-48 mx-auto rounded-lg overflow-hidden">
                        <Image
                          src={referenceImage || "/placeholder.svg"}
                          alt="Photo de référence"
                          fill
                          className="object-cover"
                        />
                      </div>
                      <Button variant="outline" size="sm" onClick={() => setReferenceImage(null)}>
                        Changer de photo
                      </Button>
                    </div>
                  ) : (
                    <>
                      <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                      <h3 className="font-semibold mb-2">Sélectionnez une photo de vous</h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Choisissez une photo claire où votre visage est visible
                      </p>
                      <Input
                        type="file"
                        accept="image/jpeg,image/png,image/jpg"
                        onChange={handleReferenceUpload}
                        className="max-w-xs mx-auto"
                      />
                    </>
                  )}
                </div>

                {referenceImage && (
                  <Button size="lg" className="w-full" onClick={handleSearch} disabled={searching}>
                    {searching ? (
                      <>
                        <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                        Recherche en cours...
                      </>
                    ) : (
                      <>
                        <Search className="h-5 w-5 mr-2" />
                        Rechercher mes photos
                      </>
                    )}
                  </Button>
                )}

                <div className="bg-muted/50 rounded-lg p-4">
                  <h4 className="font-semibold mb-2 text-sm">Conseils pour une meilleure recherche:</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Utilisez une photo récente</li>
                    <li>• Assurez-vous que votre visage est bien éclairé</li>
                    <li>• Évitez les lunettes de soleil ou accessoires cachant le visage</li>
                  </ul>
                </div>
              </div>
            </Card>
          )}

          {step === "results" && (
            <div className="space-y-6">
              <Card className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold mb-1">Résultats de la recherche</h2>
                    <p className="text-muted-foreground">{matchedPhotos.length} photo(s) trouvée(s)</p>
                  </div>
                  <Button variant="outline" onClick={() => setStep("upload")}>
                    Nouvelle recherche
                  </Button>
                </div>
              </Card>

              {matchedPhotos.length > 0 ? (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {matchedPhotos.map((photo, index) => (
                      <Card key={index} className="overflow-hidden group">
                        <div className="relative aspect-square">
                          <Image
                            src={photo || "/placeholder.svg"}
                            alt={`Photo ${index + 1}`}
                            fill
                            className="object-cover"
                          />
                          <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                            <Button size="sm" variant="secondary">
                              <Download className="h-4 w-4 mr-2" />
                              Télécharger
                            </Button>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>

                  <Card className="p-6">
                    <Button size="lg" className="w-full">
                      <Download className="h-5 w-5 mr-2" />
                      Télécharger toutes les photos ({matchedPhotos.length})
                    </Button>
                  </Card>
                </>
              ) : (
                <Card className="p-12 text-center">
                  <p className="text-muted-foreground">
                    Aucune photo trouvée. Essayez avec une autre photo de référence.
                  </p>
                </Card>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
