import Link from "next/link"
import { Camera, Search, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Header */}
      <header className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-bold">FaceFind</h1>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center mb-16">
          <h2 className="text-5xl font-bold mb-6 text-balance">Retrouvez vos photos d'événements en un instant</h2>
          <p className="text-xl text-muted-foreground text-balance mb-8">
            Grâce à la reconnaissance faciale, trouvez toutes vos photos d'événements automatiquement
          </p>
        </div>

        {/* Role Selection Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Producer Card */}
          <Card className="p-8 hover:shadow-lg transition-shadow">
            <div className="flex flex-col items-center text-center gap-6">
              <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                <Camera className="h-8 w-8 text-primary" />
              </div>
              <div>
                <h3 className="text-2xl font-bold mb-2">Producer</h3>
                <p className="text-muted-foreground mb-6">Vous êtes photographe ? Uploadez vos photos d'événements</p>
              </div>
              <Link href="/producer" className="w-full">
                <Button size="lg" className="w-full">
                  Accéder à l'espace Producer
                </Button>
              </Link>
            </div>
          </Card>

          {/* Consumer Card */}
          <Card className="p-8 hover:shadow-lg transition-shadow">
            <div className="flex flex-col items-center text-center gap-6">
              <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                <Search className="h-8 w-8 text-primary" />
              </div>
              <div>
                <h3 className="text-2xl font-bold mb-2">Consumer</h3>
                <p className="text-muted-foreground mb-6">
                  Vous cherchez vos photos ? Trouvez-les par reconnaissance faciale
                </p>
              </div>
              <Link href="/consumer" className="w-full">
                <Button size="lg" variant="outline" className="w-full bg-transparent">
                  Accéder à l'espace Consumer
                </Button>
              </Link>
            </div>
          </Card>
        </div>

        {/* Features Section */}
        <div className="mt-24 max-w-4xl mx-auto">
          <h3 className="text-3xl font-bold text-center mb-12">Comment ça marche ?</h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold text-primary">1</span>
              </div>
              <h4 className="font-semibold mb-2">Upload</h4>
              <p className="text-sm text-muted-foreground">Les photographes uploadent les photos de l'événement</p>
            </div>
            <div className="text-center">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold text-primary">2</span>
              </div>
              <h4 className="font-semibold mb-2">Analyse</h4>
              <p className="text-sm text-muted-foreground">Notre IA analyse automatiquement tous les visages</p>
            </div>
            <div className="text-center">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold text-primary">3</span>
              </div>
              <h4 className="font-semibold mb-2">Trouvez</h4>
              <p className="text-sm text-muted-foreground">Uploadez votre photo et retrouvez toutes vos photos</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t mt-24 py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© 2025 FaceFind - Service de reconnaissance faciale pour événements</p>
        </div>
      </footer>
    </div>
  )
}
