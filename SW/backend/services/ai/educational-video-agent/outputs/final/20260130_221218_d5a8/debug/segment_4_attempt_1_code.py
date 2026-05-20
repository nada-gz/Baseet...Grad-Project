from manim import *

class ImportanceOfSustainableEnergy(Scene):
    def construct(self):
        # Titles
        english_title = Text("Importance of Sustainable Energy", font_size=40).to_edge(UP)
        arabic_title = Text("أهمية الطاقة المستدامة", font="Arial", font_size=32).next_to(english_title, DOWN, buff=0.3)
        
        self.play(FadeIn(english_title), FadeIn(arabic_title))
        self.wait(2)

        # First idea: Fossil fuels produce harmful emissions
        fossil_fuels = Text("Fossil Fuels -> Harmful Emissions", font_size=32).move_to(ORIGIN)
        self.play(FadeIn(fossil_fuels))
        self.wait(3)

        # Transition to sustainable energy
        sustainable_energy = Text("Sustainable Energy Sources", font_size=32).move_to(ORIGIN)
        self.play(FadeOut(fossil_fuels), FadeIn(sustainable_energy))
        self.wait(2)

        # Show solar and wind as solutions
        solar_icon = Circle(radius=0.5, color=ORANGE).shift(LEFT*2)
        wind_icon = Circle(radius=0.5, color=BLUE).shift(RIGHT*2)
        solar_text = Text("Solar", font_size=24).next_to(solar_icon, DOWN)
        wind_text = Text("Wind", font_size=24).next_to(wind_icon, DOWN)

        self.play(Create(solar_icon), Create(wind_icon), FadeIn(solar_text), FadeIn(wind_text))
        self.wait(3)

        # Combine into equation-like structure
        equation = MathTex("Solar + Wind = ", "Clean Energy", font_size=36).move_to(ORIGIN)
        self.play(ReplacementTransform(sustainable_energy, equation[0]))
        self.wait(2)

        # Add final result
        clean_energy = Text("Reduced Pollution", font_size=32).next_to(equation, DOWN)
        self.play(FadeIn(clean_energy))
        self.wait(3)

        # Final summary
        summary = Text("Helps Future Generations", font_size=32).move_to(ORIGIN)
        self.play(FadeOut(equation), FadeOut(clean_energy), FadeIn(summary))
        self.wait(3)

        # Cleanup
        self.play(FadeOut(summary), FadeOut(solar_icon), FadeOut(wind_icon), FadeOut(solar_text), FadeOut(wind_text))
        self.wait(1)