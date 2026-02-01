from manim import *

class StellarClassification(Scene):
    def construct(self):
        # Titles
        english_title = Text("Types of Stars by Color and Temperature", font_size=40).to_edge(UP)
        arabic_title = Text("تصنيف النجوم حسب اللون والحرارة", font="Arial", font_size=32).next_to(english_title, DOWN, buff=0.3)
        
        self.play(FadeIn(english_title), FadeIn(arabic_title))
        self.wait(2)

        # Temperature scale
        temp_scale = NumberLine(
            x_range=[0, 50000, 10000],
            length=10,
            include_numbers=True,
            label_direction=UP,
            numbers_to_show=6
        )
        temp_scale.next_to(ORIGIN, DOWN, buff=1.5)
        temp_labels = ["3000K", "10000K", "20000K", "30000K", "40000K", "50000K"]
        temp_label_objs = [Text(label, font_size=24) for label in temp_labels]
        for i, label in enumerate(temp_label_objs):
            label.next_to(temp_scale.n2p(i*10000), DOWN)
        
        self.play(Create(temp_scale), *[FadeIn(label) for label in temp_label_objs])
        self.wait(2)

        # Star color indicators
        blue_star = Circle(radius=0.5, color=BLUE).move_to(temp_scale.n2p(45000))
        yellow_star = Circle(radius=0.5, color=YELLOW).move_to(temp_scale.n2p(25000))
        red_star = Circle(radius=0.5, color=RED).move_to(temp_scale.n2p(5000))

        blue_text = Text("Blue Star\n>30,000K", font_size=24).next_to(blue_star, UP)
        yellow_text = Text("Yellow Star\n~5,800K", font_size=24).next_to(yellow_star, UP)
        red_text = Text("Red Star\n~3,000K", font_size=24).next_to(red_star, UP)

        self.play(FadeIn(blue_star), FadeIn(blue_text))
        self.wait(2)
        self.play(FadeIn(yellow_star), FadeIn(yellow_text))
        self.wait(2)
        self.play(FadeIn(red_star), FadeIn(red_text))
        self.wait(3)

        # Explanation text
        explanation = Text("Hotter stars emit more energy and fuse faster.", font_size=28).move_to(ORIGIN)
        self.play(FadeIn(explanation))
        self.wait(4)

        # Cleanup
        self.play(FadeOut(blue_star), FadeOut(yellow_star), FadeOut(red_star),
                  FadeOut(blue_text), FadeOut(yellow_text), FadeOut(red_text),
                  FadeOut(temp_scale), *[FadeOut(label) for label in temp_label_objs],
                  FadeOut(explanation))
        self.wait(1)

        # Final title fade out
        self.play(FadeOut(english_title), FadeOut(arabic_title))
        self.wait(1)