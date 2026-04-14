from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle

PRIMARY_RED = HexColor("#D93025")
SOFT_BLACK = HexColor("#1A1A1A")
DARK_GRAY = HexColor("#737373")
BEIGE_BG = HexColor("#F7F5F2")
WHITE = HexColor("#FFFFFF")
PAGE_WIDTH, PAGE_HEIGHT = A4


class SnapchatMarketingPDF:
    def __init__(self, filename):
        self.canvas = canvas.Canvas(filename, pagesize=A4)
        self.width = PAGE_WIDTH
        self.height = PAGE_HEIGHT

    def _header(self, page_num=None):
        self.canvas.setStrokeColor(PRIMARY_RED)
        self.canvas.setLineWidth(3)
        self.canvas.line(0, self.height - 20, self.width, self.height - 20)
        self.canvas.setFillColor(PRIMARY_RED)
        self.canvas.roundRect(20, self.height - 55, 35, 30, 5, fill=1, stroke=0)
        self.canvas.setFillColor(WHITE)
        self.canvas.setFont("Helvetica-Bold", 16)
        self.canvas.drawString(25, self.height - 40, "B2")
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawString(60, self.height - 42, "BENE")
        self.canvas.setFillColor(PRIMARY_RED)
        self.canvas.setFont("Helvetica-Bold", 10)
        self.canvas.drawString(108, self.height - 38, "2")
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawString(115, self.height - 42, "LUXE")
        if page_num:
            self.canvas.setFillColor(DARK_GRAY)
            self.canvas.setFont("Helvetica", 9)
            self.canvas.drawRightString(
                self.width - 20, self.height - 40, f"Page {page_num}/6"
            )
        return self.height - 70

    def _placeholder(self, x, y, w, h, lbl):
        self.canvas.setStrokeColor(DARK_GRAY)
        self.canvas.setLineWidth(1)
        self.canvas.setDash(4, 4)
        self.canvas.rect(x, y, w, h)
        self.canvas.setDash(1, 0)
        self.canvas.setFillColor(DARK_GRAY)
        self.canvas.setFont("Helvetica-Oblique", 9)
        self.canvas.drawCentredString(x + w / 2, y + h / 2 - 5, f"[{lbl}]")
        self.canvas.setFont("Helvetica", 8)
        self.canvas.drawCentredString(x + w / 2, y + h / 2 + 8, "Ajouter capture écran")

    def _check(self, x, y, txt, chk=False):
        sz = 12
        self.canvas.setStrokeColor(PRIMARY_RED)
        self.canvas.setLineWidth(1.5)
        self.canvas.rect(x, y - sz, sz, sz)
        if chk:
            self.canvas.setFillColor(PRIMARY_RED)
            self.canvas.setFont("Helvetica-Bold", 10)
            self.canvas.drawString(x + 2, y - 10, "✓")
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(x + 18, y - 10, txt)
        return y - 25

    def _p1(self):
        self.canvas.showPage()
        self.canvas.setFillColor(WHITE)
        self.canvas.rect(0, 0, self.width, self.height, fill=1)
        self.canvas.setFillColor(PRIMARY_RED)
        self.canvas.setStrokeColor(PRIMARY_RED)
        self.canvas.setLineWidth(60)
        self.canvas.arc(150, 500, 300, 300, 0, 360)
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica-Bold", 32)
        self.canvas.drawCentredString(self.width / 2, 350, "Analyse Marketing")
        self.canvas.setFont("Helvetica-Bold", 36)
        self.canvas.drawCentredString(self.width / 2, 300, "Snapchat")
        self.canvas.setFillColor(PRIMARY_RED)
        self.canvas.setFont("Helvetica-Bold", 28)
        self.canvas.drawCentredString(self.width / 2, 240, "RIFI NPK")
        self.canvas.setFillColor(BEIGE_BG)
        self.canvas.roundRect(self.width / 2 - 80, 190, 160, 35, 10, fill=1, stroke=0)
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawCentredString(self.width / 2, 205, "Compte Bene2Luxe")
        self.canvas.setStrokeColor(PRIMARY_RED)
        self.canvas.setLineWidth(2)
        self.canvas.line(self.width / 2 - 100, 170, self.width / 2 + 100, 170)
        self.canvas.setFillColor(DARK_GRAY)
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawCentredString(
            self.width / 2, 120, "Document interne • Analyse des performances"
        )
        self.canvas.drawCentredString(self.width / 2, 100, "Avril 2026")
        self.canvas.setFillColor(PRIMARY_RED)
        self.canvas.setFont("Helvetica-Bold", 10)
        self.canvas.drawCentredString(self.width / 2, 60, "1 / 6")
        self._header()

    def _p2(self):
        self.canvas.showPage()
        self.canvas.setFillColor(WHITE)
        self.canvas.rect(0, 0, self.width, self.height, fill=1)
        y = self._header(page_num=2)
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica-Bold", 22)
        self.canvas.drawString(20, y - 10, "💬 Conversations Clients")
        y -= 50
        cats = [
            ("C'est fiable ?", "Questions sur l'authenticité et la confiance"),
            ("C'est quoi la qualité ?", "Demandes de détails sur l'état des articles"),
            ("Ça taille comment ?", "Questions sur les tailles et ajustements"),
            ("C'est combien ?", "Demandes de prix et disponibilité"),
        ]
        for i, (c, d) in enumerate(cats):
            x = 20 if i % 2 == 0 else self.width / 2 + 10
            yp = y - (i // 2) * 90 - 10
            self.canvas.setFillColor(PRIMARY_RED)
            self.canvas.setFont("Helvetica-Bold", 13)
            self.canvas.drawString(x, yp, f"❓ {c}")
            self.canvas.setFillColor(SOFT_BLACK)
            self.canvas.setFont("Helvetica", 10)
            self.canvas.drawString(x, yp - 18, d)
            self._placeholder(x, yp - 80, self.width / 2 - 30, 55, "Écran")
        y -= 200
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawString(20, y, "Comportements Clients")
        y -= 25
        for b in [
            "Clients qui hésitent → suivre avec message de suivi",
            "Clients qui disparaissent → relance après 2-3 jours",
            "Clients qui négocient → avoir une marge de manœuvre prête",
            "Clients qui achètent → demander photo de réception",
        ]:
            y = self._check(25, y, b)

    def _p3(self):
        self.canvas.showPage()
        self.canvas.setFillColor(WHITE)
        self.canvas.rect(0, 0, self.width, self.height, fill=1)
        y = self._header(page_num=3)
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica-Bold", 22)
        self.canvas.drawString(20, y - 10, "🚫 Objections Clients")
        y -= 40
        self.canvas.setFillColor(DARK_GRAY)
        self.canvas.setFont("Helvetica", 11)
        self.canvas.drawString(20, y, "Ce que les gens disent AVANT d'acheter")
        y -= 30
        objs = [
            (
                '😰 "J\'ai peur"',
                "Réponse: Garantie authentique, photos détaillées, avis clients",
            ),
            (
                '🤔 "Je réfléchis"',
                "Réponse: OK, je reste disponible. Envoyer catalogue complet.",
            ),
            (
                '⏰ "Plus tard"',
                "Réponse: Pas de souci. Prévenir des nouvelles arrivées.",
            ),
            (
                '💰 "C\'est cher"',
                "Réponse: Comparer avec prix marché. Qualité justifier prix.",
            ),
            (
                '❓ "Je connais pas"',
                "Réponse: Expliquer la marque, l'histoire, la valeur.",
            ),
        ]
        for o, r in objs:
            self.canvas.setFillColor(BEIGE_BG)
            self.canvas.roundRect(20, y - 25, self.width - 40, 30, 5, fill=1, stroke=0)
            self.canvas.setFillColor(PRIMARY_RED)
            self.canvas.setFont("Helvetica-Bold", 12)
            self.canvas.drawString(30, y - 12, o)
            y -= 35
            self.canvas.setFillColor(SOFT_BLACK)
            self.canvas.setFont("Helvetica", 10)
            self.canvas.drawString(30, y, f"→ {r}")
            y -= 40
        y -= 20
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawString(20, y, "💡 Conseils")
        y -= 20
        for t in [
            "Toujours répondre dans les 30 minutes",
            "Personnaliser les réponses selon le client",
            "Suivre les objections pour améliorer l'argumentaire",
            "Noter les objections fréquentes pour adapter le discours",
        ]:
            self.canvas.setFillColor(SOFT_BLACK)
            self.canvas.setFont("Helvetica", 10)
            self.canvas.drawString(30, y, f"✓ {t}")
            y -= 18

    def _p4(self):
        self.canvas.showPage()
        self.canvas.setFillColor(WHITE)
        self.canvas.rect(0, 0, self.width, self.height, fill=1)
        y = self._header(page_num=4)
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica-Bold", 22)
        self.canvas.drawString(20, y - 10, "📸 Preuves de Ventes")
        y -= 40
        self.canvas.setFillColor(DARK_GRAY)
        self.canvas.setFont("Helvetica", 11)
        self.canvas.drawString(
            20, y, "Collecter les témoignages pour renforcer la confiance"
        )
        y -= 30
        cats = [
            ("📦 Screenshots Commandes", "Captures des conversations de vente"),
            ("💳 Paiements", "Preuves de virement ou paiement"),
            ('✉️ "J\'ai reçu"', "Messages de confirmation de réception"),
            ("📸 Photos Clients", "Photos des clients avec leurs achats"),
        ]
        for i, (c, d) in enumerate(cats):
            yp = y - i * 110
            self.canvas.setFillColor(SOFT_BLACK)
            self.canvas.setFont("Helvetica-Bold", 13)
            self.canvas.drawString(20, yp, c)
            self.canvas.setFillColor(DARK_GRAY)
            self.canvas.setFont("Helvetica", 10)
            self.canvas.drawString(20, yp - 15, d)
            self._placeholder(20, yp - 80, self.width - 40, 60, c.split()[0])
        y -= 470
        self.canvas.setFillColor(PRIMARY_RED)
        self.canvas.setFont("Helvetica-Bold", 12)
        self.canvas.drawString(20, y, "💡 Utiliser les preuves dans les Stories!")
        y -= 20
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(
            20,
            y,
            "Les témoignages boostent la crédibilité et aident les indécis à franchir le pas.",
        )

    def _p5(self):
        self.canvas.showPage()
        self.canvas.setFillColor(WHITE)
        self.canvas.rect(0, 0, self.width, self.height, fill=1)
        y = self._header(page_num=5)
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica-Bold", 22)
        self.canvas.drawString(20, y - 10, "📊 Résultats Stories Snapchat")
        y -= 45
        self.canvas.setFillColor(WHITE)
        self.canvas.roundRect(
            15,
            y - 180,
            self.width - 30,
            175,
            10,
            fill=1,
            stroke=PRIMARY_RED,
            lineWidth=1,
        )
        self.canvas.setFillColor(PRIMARY_RED)
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawString(25, y - 15, "✅ Ce qui marche bien")
        good = [
            "📸 Photos produits en direct",
            "🎥 Vidéos déballage",
            "⏰ Countdown offres",
            "💬 Poll interactif",
            '🛍️ Stories "achat possible maintenant"',
        ]
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica", 11)
        for i, itm in enumerate(good):
            self.canvas.drawString(35, y - 40 - i * 20, itm)
        y -= 200
        self.canvas.setFillColor(WHITE)
        self.canvas.roundRect(
            15,
            y - 130,
            self.width - 30,
            125,
            10,
            fill=1,
            stroke=PRIMARY_RED,
            lineWidth=1,
        )
        self.canvas.setFillColor(PRIMARY_RED)
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawString(25, y + 10, "❌ Ce qui flop")
        bad = [
            "📝 Trop de texte",
            "🎬 Vidéos trop longues",
            "🖼️ Photos floues ou mal éclairées",
            "⏸️ Stories sans call-to-action",
        ]
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica", 11)
        for i, itm in enumerate(bad):
            self.canvas.drawString(35, y - 15 - i * 20, itm)
        y -= 150
        self.canvas.setFillColor(BEIGE_BG)
        self.canvas.roundRect(15, y - 60, self.width - 30, 55, 8, fill=1, stroke=0)
        self.canvas.setFillColor(DARK_GRAY)
        self.canvas.setFont("Helvetica-Oblique", 10)
        self.canvas.drawCentredString(
            self.width / 2, y - 25, "[Captures analytics Snapchat]"
        )
        self.canvas.setFont("Helvetica", 9)
        self.canvas.drawCentredString(
            self.width / 2, y - 40, "Ajouter screenshots des statistiques Stories"
        )

    def _p6(self):
        self.canvas.showPage()
        self.canvas.setFillColor(WHITE)
        self.canvas.rect(0, 0, self.width, self.height, fill=1)
        y = self._header(page_num=6)
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica-Bold", 22)
        self.canvas.drawString(20, y - 10, "📈 Métriques Clés")
        y -= 40
        self.canvas.setFillColor(DARK_GRAY)
        self.canvas.setFont("Helvetica", 11)
        self.canvas.drawString(
            20, y, "Suivre ces chiffres pour optimiser les performances"
        )
        y -= 35
        mets = [
            ("💰", "Nombre de ventes", "Ventes confirmées par mois"),
            ("💬", "Nombre de messages", "Conversations ouvertes"),
            ("👁️", "Nombre de vues", "Vues Stories et publications"),
            ("📊", "Taux de conversion", "Messages → Ventes (%)"),
        ]
        for i, (ic, t, d) in enumerate(mets):
            x = 20 if i % 2 == 0 else self.width / 2 + 10
            yp = y - (i // 2) * 95 - 15
            self.canvas.setFillColor(BEIGE_BG)
            bw = self.width / 2 - 30
            self.canvas.roundRect(x, yp - 65, bw, 70, 8, fill=1, stroke=0)
            self.canvas.setFillColor(PRIMARY_RED)
            self.canvas.setFont("Helvetica-Bold", 20)
            self.canvas.drawString(x + 10, yp - 5, ic)
            self.canvas.setFillColor(SOFT_BLACK)
            self.canvas.setFont("Helvetica-Bold", 18)
            self.canvas.drawString(x + 40, yp - 5, "---")
            self.canvas.setFont("Helvetica-Bold", 12)
            self.canvas.drawString(x + 10, yp - 25, t)
            self.canvas.setFillColor(DARK_GRAY)
            self.canvas.setFont("Helvetica", 9)
            self.canvas.drawString(x + 10, yp - 40, d)
            self.canvas.setStrokeColor(DARK_GRAY)
            self.canvas.setLineWidth(1)
            self.canvas.setDash(3, 3)
            self.canvas.line(x + 10, yp - 50, x + bw - 10, yp - 50)
        y -= 210
        self.canvas.setFillColor(SOFT_BLACK)
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawString(20, y, "🎯 Objectifs à atteindre")
        y -= 25
        for g in [
            "Répondre en moins de 30 minutes",
            "Au moins 5 ventes par semaine",
            "Taux de conversion minimum 15%",
            "100+ vues par Story",
        ]:
            y = self._check(25, y, g)
            y -= 5
        self.canvas.setFillColor(DARK_GRAY)
        self.canvas.setFont("Helvetica", 9)
        self.canvas.drawCentredString(
            self.width / 2, 30, "Document généré pour Rida • Bene2Luxe • Avril 2026"
        )

    def generate(self):
        self._p1()
        self._p2()
        self._p3()
        self._p4()
        self._p5()
        self._p6()
        self.canvas.save()
        print("PDF généré: snapchat_analysis_rifi_npk.pdf")


if __name__ == "__main__":
    SnapchatMarketingPDF("snapchat_analysis_rifi_npk.pdf").generate()
