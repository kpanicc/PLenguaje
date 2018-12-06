from antlr4 import *
from moomaListener import moomaListener
from moomaParser import moomaParser


class Language:
    def __init__(self, ident):
        self.ident = ident
        self.inputs = []
        self.outputs = []

    def existInput(self, _input):
        return True if _input in self.inputs else False

    def existOutput(self, output):
        return True if output in self.outputs else False

    def __eq__(self, other):
        return other == self.ident

    def __str__(self):
        retval = "{}:\nInputs: ".format(self.ident)
        for x in self.inputs:
            retval += "{}\t".format(x)
        retval += "\nOutputs: "
        for x in self.outputs:
            retval += "{}\t".format(x)
        return retval

class Automaton:
    def __init__(self, ident, language):
        self.ident = ident
        self.states = {}
        self.transitions = []
        self.language = language
        self.initial = None

    def addinitial(self, state):
        if state in self.states:
            self.initial = state

    def __eq__(self, other):
        return other == self.ident

    def __str__(self):
        retval = "{}:\nStates: ".format(self.ident)
        for x, y in self.states.items():
            retval += "{}:{}\t".format(x, y)
        retval += "\nInitial: {}".format(self.initial)
        retval += "\nLanguage: {}".format(self.language)
        retval += "\nTransitions:\n"
        for x in self.transitions:
            retval += "\t{}\n".format(str(x))
        return retval


class Transition:
    def __init__(self, origin, event, dest):
        self.origin = origin
        self.event = event
        self.dest = dest

    def __str__(self):
        return "{}|{} -> {}".format(self.origin, self.event, self.dest)



class MyMoomaListener(moomaListener):
    def __init__(self, file):
        self.file = open(file, "w")
        self.languages = []
        self.automatons = []
        self.outputs = {}

        self.env = None
        self.error = False

    def exitProgram(self, ctx:moomaParser.ProgramContext):

        print("Lenguajes: ")
        for lang in self.languages:
            print(lang)
        print("\n\n\nAutomatas: ")
        for aut in self.automatons:
            print(aut)
        print("\n\n\noutputs: ")
        for key, value in self.outputs.items():
            print("{}: {}".format(key, value))
        print("\n\n\nEnv: {}\nError: {}".format(self.env, self.error))

        self.file.write("import {};".format(self.env))


    def enterEnvironment(self, ctx:moomaParser.EnvironmentContext):
        self.env = str(ctx.Clase())

    def enterOutput(self, ctx:moomaParser.OutputContext):
        # Check if a code identifier has been already defined
        if str(ctx.Ident()) in self.outputs.keys():
            self.error = True
        else:
            self.outputs[ctx.Ident()] = str(ctx.Codigo())[2:-2]

    def enterDefine(self, ctx:moomaParser.DefineContext):
        # Check if a language identifier has already been defined
        if str(ctx.Ident()) in self.languages:
            self.error = True
        else:
            self.languages.append(Language(str(ctx.Ident())))

    def enterEntrada(self, ctx:moomaParser.EntradaContext):
        # The language this goes in is the last one seen due to the way we traverse the tree
        lang = self.languages[-1]
        events = ctx.l_evento().getText().split(",")
        for event in events:
            lang.inputs.append(event)

    def enterSalida(self, ctx:moomaParser.SalidaContext):
        # The language this goes in is the last one seen due to the way we traverse the tree
        lang = self.languages[-1]
        idents = ctx.l_ident().getText().split(",")
        for ident in idents:
            lang.outputs.append(ident)

    def enterAutomaton(self, ctx:moomaParser.AutomatonContext):
        # Check if this automaton identier has already been defined
        if str(ctx.Ident(0)) in self.automatons:
            self.error = True
        else:
            # Nested ifs for the future: Maybe we want to specify error messages
            # Check if the language for the automaton exists
            if str(ctx.Ident(1)) not in self.languages:
                self.error = True
            else:
                self.automatons.append(Automaton(ctx.Ident(0), ctx.Ident(1)))

    def enterStates(self, ctx:moomaParser.StatesContext):
        # The automaton this goes in is the last one seen due to the way we traverse the tree
        automaton = self.automatons[-1]
        states = ctx.l_states().getText().split(",")

        for state in states:
            state_splitted = state.split("|")
            automaton.states[str(state_splitted[0])] = str(state_splitted[1])

    def enterInitial(self, ctx:moomaParser.InitialContext):
        # The automaton this goes in is the last one seen due to the way we traverse the tree
        automaton = self.automatons[-1]
        automaton.addinitial(str(ctx.Ident()))

        if automaton.initial is None:
            self.error = True

    def enterTransitions(self, ctx:moomaParser.TransitionsContext):
        # The automaton this goes in is the last one seen due to the way we traverse the tree
        automaton = self.automatons[-1]
        transitions = ctx.l_transitions().getText().split(";")[:-1]
        for trans in transitions:
            origin = trans.split("|")[0]
            event = trans.split("|")[1].split("->")[0]
            dest = trans.split("|")[1].split("->")[1]

            automaton.transitions.append(Transition(origin, event, dest))

    def visitErrorNode(self, node:ErrorNode):
        self.error = True
