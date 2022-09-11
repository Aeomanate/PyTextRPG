from random import *
from BaseQuestuins import *


class Restart(QuestionStatic):
    def __init__(self, question=None, variants=None, game=None):
        super().__init__(question, variants)
        self.game = game

    def cook(self, array_of_arguments):
        self.game._count_dogs = choice([5, 6, 7])
        self.game.q_attack_first = MiniGame(self.game._count_dogs, self.game.player, self)
        for arg in array_of_arguments:
            if type(arg) is Player:
                arg.sword = False
                arg.shield = False
                arg.health = 100


class Player:
    def __init__(self):
        self.health = 100
        self.shield = False
        self.sword = False

    def is_alive(self):
        return self.health > 0


class SwordObrain(RhetoricQuestion):
    def cook(self, array_of_arguments):
        for arg in array_of_arguments:
            if type(arg) is Player:
                arg.sword = True


class ShieldObrain(RhetoricQuestion):
    def cook(self, array_of_arguments):
        for arg in array_of_arguments:
            if type(arg) is Player:
                arg.shield = True


class Dog:
    def __init__(self):
        self.is_damaged = False


class MiniGame(GameState):
    def __init__(self, dogs_count, player, q_restart):
        self.dogs = [Dog() for _ in range(dogs_count)]
        self.player = player
        self.dogs_damage = 15
        self.cur_message = ""
        self.cur_state_to_compute = self.attack
        self.q_restart = q_restart

    def attack(self):
        self.cur_message = "Выбрав ближайшую собаку целью, вы наносите удар деревянным мечом."
        random_dog = choice(self.dogs)

        if random_dog.is_damaged:
            self.dogs.remove(random_dog)
            return self.you_kills_dog
        else:
            random_dog.is_damaged = True
            self.player.health -= self.dogs_damage
            return self.you_hits_dog

    def you_hits_dog(self):
        self.cur_message = "Раненная собака отступает назад, но ближайшая к ней успевает вас укусить"
        return self.buttle_info

    def you_kills_dog(self):
        self.cur_message = "Ваш удар пришёлся по уже раненной собаке! Минус один противник! Стая вас боится, так держать!"
        return self.buttle_info

    def buttle_info(self):
        self.cur_message = \
            f">> Ваши потери здоровья: {self.dogs_damage}\n" \
            f">> Ваше здоровье: {self.player.health}\n" \
            f">> Собак осталось: {len(self.dogs)}"
        return self.attack

    def cook(self, array_of_arguments):
        self.cur_state_to_compute = self.cur_state_to_compute()

    def print(self):
        print(self.cur_message)
        print("1. Далее")

    def choise_next_state(self, number):
        if self.player.health <= 0:
            return RhetoricQuestion(
                question="Злая собака наносит решающий удар. Вы пали в неравном бою. Конец.",
                next_state=self.q_restart
            )
        elif len(self.dogs) == 0:
            return RhetoricQuestion(
                question="Вы победили всех собак. Собрав их тушки, вы вернулись в город и не умерли на следующий день от голода. Конец.",
                next_state=self.q_restart
            )
        else:
            return self


class Game:
    def __init__(self):
        self.player = Player()
        self._count_dogs = choice([5, 6, 7])

        q_restart = Restart()  #
        q_on_tree = QuestionStatic()  #
        q_to_town = RhetoricQuestion()  #
        q_planks = QuestionStatic()  #
        q_to_dogs = QuestionStatic()  #
        q_run_to_dogs = RhetoricQuestion()
        q_planks_home = RhetoricQuestion()  #
        q_make_sword = SwordObrain()  #
        q_make_shield = ShieldObrain()  #
        q_where_we_run = QuestionStatic()  #
        q_strawberry_win = RhetoricQuestion()  #
        q_how_to_fight = ManagerOfDynamicQuestions()  #
        q_attack_first = MiniGame(self._count_dogs, self.player, q_restart)  #
        q_observe = RhetoricQuestion()  #
        q_rest_death = RhetoricQuestion()  #
        q_dogs_feast = RhetoricQuestion()  #

        v_chop_tree = Variant("Срубить дерево", q_planks)
        q_tree_appears = QuestionStatic(question="Вы вышли из города и встретили дерево", variants=[
            Variant("Пройти мимо", q_to_dogs),
            Variant("Залезть на дерево", q_on_tree),
            v_chop_tree
        ])

        self._current_state = q_tree_appears

        q_tree_appears.__init__(question="Вы вышли из города и встретили дерево", variants=[
            Variant("Пройти мимо", q_to_dogs),
            Variant("Залезть на дерево", q_on_tree),
            v_chop_tree
        ])

        q_on_tree.__init__(
            question=lambda: f"Вы залезли на дерево и увидели вдалеке стаю из {self._count_dogs} диких собак. До них примерно 300 метров. Вволю испугавшись, вы слезли с дерева. Что будете делать дальше?",
            variants=[
                Variant("Идти к собакам", q_to_dogs),
                Variant("Бежать к собакам", q_run_to_dogs),
                v_chop_tree,
                Variant("Вернуться в город", q_to_town)
            ]
        )

        q_to_town.__init__(
            question="Вы вернулись в город и ваша ночь прошла хорошо. Но вы выходили из города, чтобы найти еду. Еды вы не нашли, потому умерли на следующий день от голода. Конец.",
            next_state=q_restart
        )

        q_restart.__init__(
            question="Попробуешь ещё раз?",
            variants=[
                Variant("Да", q_tree_appears),
                Variant("Нет", None)
            ],
            game=self
        )

        q_planks.__init__(
            question="Вы получили доски. Что будете с ними делать?",
            variants=[
                Variant("Сделать шалаш", q_planks_home),
                Variant("Сделать меч", q_make_sword),
                Variant("Сделать щит", q_make_shield)
            ]
        )

        q_planks_home.__init__(
            question="Вы сделали шалаш и устроились удобно в нём. Наступила ночь, вас нашли голодные собаки и съели. Конец.",
            next_state=q_restart
        )

        q_make_sword.__init__(
            question="Вы сделали меч и с гордой головой пошли вперёд.",
            next_state=q_to_dogs
        )

        q_make_shield.__init__(
            question="Вы сделали щит и с гордой головой пошли вперёд.",
            next_state=q_to_dogs
        )

        q_run_to_dogs.__init__(
            question="Вы побежали, что было сил. Пробежав двести метров, вы замечаете, что ваши силы на исходе. Устав, вы падаете ничком и засыпаете. Злые собаки, услышав ваш храп, пришли и съели вас. Конец.",
            next_state=q_restart
        )

        q_where_we_run.__init__(
            question="Куда?",
            variants=[
                Variant("В город, обратно!", q_to_town),
                Variant("Дальше в лес!", q_strawberry_win)
            ]
        )

        q_strawberry_win.__init__(
            question="Вы прорвались сквозь стаю собак, оббежав их по дуге. Спрятавшись за густыми деревьями, вы углубились в чащу. Обнаружив через несколько часов блужданий клубнику, вы довольный вернулись в город и не умерли на следующий день от голода. Конец",
            next_state=q_restart
        )

        q_to_dogs.__init__(
            question=f"Через 300 метров вы встречаете {self._count_dogs} злых собак. Что будете делать?",
            variants=[
                Variant("Биться!", q_how_to_fight),
                Variant("Бежать!", q_where_we_run)
            ]
        )

        q_how_to_fight.__init__(
            questions=[
                QuestionDynamicWithVariantsStatic(
                    "У вас есть меч. Вы наблюдаете, как собаки с опаской приближаются к вам. Что будете делать?",
                    condition_func=lambda player: player.sword,
                    variants=[
                        Variant("Бежать", q_where_we_run),
                        Variant("Напасть первым", q_attack_first),
                        Variant("Наблюдать", q_observe),
                    ]
                ),
                RhetoricDynamicQuestion(
                    question="У вас есть щит. Вы наблюдаете, как собаки с опаской приближаются к вам.",
                    condition_func=lambda player: player.shield,
                    next_state=q_rest_death
                ),

                RhetoricDynamicQuestion(
                    question="У вас ничего с собой нет.",
                    condition_func=lambda player: not player.sword and not player.shield,
                    next_state=q_dogs_feast
                )
            ]
        )

        q_observe.__init__(
            question="Две собаки кидаются на вас с разных сторон, одна отгрызает руку, в которой вы держите меч. Наблюдая за обильной кровопотерей, вы и собаки понимаете, кто победит в этой схватке. Конец.",
            next_state=q_restart
        )

        q_rest_death.__init__(
            question="Вы понимаете, что не сможете победить со щитом, потому решаете прорваться сквозь стаю, прикрываясь им. Вам это с успехом удалось, но когда вы уже почувствовали, что оторвались от стаи, и присели отдохнуть из-за тяжести щита, сзади на вас напала самая выносливая собака из той стаи. Смерть была быстрой и мучительной. Конец.",
            next_state=q_restart
        )

        q_dogs_feast.__init__(
            question="Собаки не увидели в вас опасности. Вожак накинулся на вас и остальные его поддержали. До вечера от вас не осталось ни косточки.",
            next_state=q_restart
        )

    def start_loop(self):
        while self._current_state is not None:
            self._current_state.cook([self.player])
            self._current_state.print()
            self._current_state = self._current_state.choise_next_state(int(input("Ваш вариант: ")))
