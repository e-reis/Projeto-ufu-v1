from random import choices, randint, randrange, random
from typing import List, Optional, Callable, Tuple

# Definindo os tipos

# genoma: uma lista de inteiros (0s e 1s)
Genome = List[int]

# população: uma lista de genomas
Population = List[Genome]

# Callable: é um tipo genérico da biblioteca typing do Python que indica que um objeto pode ser chamado como uma função.

# Estou definindo a função que gera uma população.
PopulateFunc = Callable[[], Population]

# Estou definindo a função que avalia um genoma retorna um valor inteiro.
FitnessFunc = Callable[[Genome], int]

# Estou definindo a função que seleciona dois indivíduos da população.
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]

# Estou definindo a função que realiza o cruzamento de dois genomas.
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]

# Estou definindo a função que aplica mutação a um genoma.
MutationFunc = Callable[[Genome], Genome]

# Estou definindo a função que imprime as estatísticas do algoritmo.
PrinterFunc = Callable[[Population, int, FitnessFunc], None]

# Estou criando um genoma binário aleatório, de tamanho "length", composto de genes (bits) 0s e 1s.
def generate_genome(length: int) -> Genome:
    return choices([0, 1], k=length)

# Estou criando uma população de "tamanho: size" indivíduos (genomas) de tamanho "genome_length" bits.
def generate_population(size: int, genome_length: int) -> Population:
    return [generate_genome(genome_length) for _ in range(size)]

# Estou escolhendo um ponto aleatório "p" que faz a troca de partes dos pais para gerar dois filhos.
def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    if len(a) != len(b):
        raise ValueError("Genomes a and b must be of same length")

    length = len(a)
    if length < 2:
        return a, b

    p = randint(1, length - 1)
    return a[0:p] + b[p:], b[0:p] + a[p:]

# Estou escolhendo um índice aleatório "index" e trocando o valor do gene nesse índice por 0 ou 1 (ou vice-versa) em cada mutação.
# abs(genome[index] - 1) é usado para inverter o valor do bit no genoma binário:
# abs(0 - 1) = abs(-1) = 1  , Troca 0 por 1
# abs(1 - 1) = abs(0) = 0  , Troca 1 por 0
def mutation(genome: Genome, num: int = 1, probability: float = 0.5) -> Genome:
    for _ in range(num):
        index = randrange(len(genome))
        genome[index] = genome[index] if random() > probability else abs(genome[index] - 1)
    return genome

# Estou somando os valores da "função fitness" de todos os genomas da população.
# A função fitness avalia a qualidade de um indivíduo dentro de um algoritmo genético.
# A função fitness atribui um valor numérico a cada genoma (candidato à solução), indicando quão bem ele se adapta ao problema em questão.
# A função fitness é a soma dos bits 1 no genoma. 
# A função population_fitness calcula a soma dos valores da função fitness de todos os genomas na população.
def population_fitness(population: Population, fitness_func: FitnessFunc) -> int:
    return sum([fitness_func(genome) for genome in population])

# Estou escolhando dois pais, dando mais chances aos indivíduos com maior fitness.
def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    return choices(
        population=population,
        weights=[fitness_func(gene) for gene in population],
        k=2
    )

# Estou ordenando a população de acordo com a função fitness, do melhor para o pior.
def sort_population(population: Population, fitness_func: FitnessFunc) -> Population:
    return sorted(population, key=fitness_func, reverse=True)

# Transforma uma lista de 0s e 1s em uma string ([1, 0, 1] → "101").
def genome_to_string(genome: Genome) -> str:
    return "".join(map(str, genome))

# Estou exibindo as estatísticas de cada geração: fitness médio, melhor e pior indivíduo.
def print_stats(population: Population, generation_id: int, fitness_func: FitnessFunc):
    print("GENERATION %02d" % generation_id)
    print("=============")
    print("Population: [%s]" % ", ".join([genome_to_string(gene) for gene in population]))
    print("Avg. Fitness: %f" % (population_fitness(population, fitness_func) / len(population)))
    sorted_population = sort_population(population, fitness_func)
    print(
        "Best: %s (%f)" % (genome_to_string(sorted_population[0]), fitness_func(sorted_population[0])))
    print("Worst: %s (%f)" % (genome_to_string(sorted_population[-1]),
                              fitness_func(sorted_population[-1])))
    print("")

    return sorted_population[0]

# Estou executando a função de evolução, que gera a população, avalia a função fitness, seleciona os melhores indivíduos, realiza o cruzamento e a mutação.
# Ação 1: gerar a população inicial.
# Ação 2: iterar até o fitness limite ser alcançado ou o número máximo de gerações (generation_limit).
# Ação 3: selecionar os melhores indivíduos e aplicar crossover e mutação.
# Extra: Imprime as estatísticas se printer for fornecido e retorna a população final e o número de gerações.
def run_evolution(
        populate_func: PopulateFunc,
        fitness_func: FitnessFunc,
        fitness_limit: int,
        selection_func: SelectionFunc = selection_pair,
        crossover_func: CrossoverFunc = single_point_crossover,
        mutation_func: MutationFunc = mutation,
        generation_limit: int = 100,
        printer: Optional[PrinterFunc] = None) \
        -> Tuple[Population, int]:
    population = populate_func()

    for i in range(generation_limit):
        population = sorted(population, key=lambda genome: fitness_func(genome), reverse=True)

        if printer is not None:
            printer(population, i, fitness_func)

        if fitness_func(population[0]) >= fitness_limit:
            break

        next_generation = population[0:2]

        for j in range(int(len(population) / 2) - 1):
            parents = selection_func(population, fitness_func)
            offspring_a, offspring_b = crossover_func(parents[0], parents[1])
            offspring_a = mutation_func(offspring_a)
            offspring_b = mutation_func(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation

    return population, i

# Exemplo de função fitness (soma dos bits 1 no genoma)
# Conta o número de 1s no genoma (quanto mais 1s, melhor o fitness).
def fitness_function(genome: Genome) -> int:
    return sum(genome)

# Parâmetros
population_size = 10
genome_length = 8
fitness_limit = genome_length  # Objetivo: maximizar o número de 1s

# Rodar a evolução
final_population, generations = run_evolution(
    lambda: generate_population(population_size, genome_length),
    fitness_function,
    fitness_limit,
    generation_limit=100,
    printer=print_stats
)

print(f"Finalizado em {generations} gerações!")

# RESULTADOS
# Criar uma população de 10 indivíduos com genomas de 8 bits.
# O objetivo é atingir 8 bits 1 (11111111).
# Finaliza quando encontra um genoma "esperado/ótimo" ou atingir 100 gerações.