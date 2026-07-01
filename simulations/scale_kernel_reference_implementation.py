"""
Scale Kernel Research Program

Reference Implementation

Version: 0.1.0

This file contains the first reference implementation of the
Scale Kernel conceptual framework.

Its purpose is not to simulate any specific real-world system,
but to demonstrate the behavior of the Scale Kernel under a
minimal set of axioms, constraints, and interaction rules.

Author: Linces Marques
"""
import random
import math
import time
import os

class Agent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.memory = 0.0          # A4: Persistência de Informação (0.0 a 1.0)
        self.base_threshold = 0.28  # Limiar base de ativação (um único vizinho de 0.35 ativa)
        self.active = False        # A6: Papel atual (ativo=causa, inativo=consequência/repouso)
        self.next_active = False   # Estado para o próximo ciclo
        self.neighbors = []        # A2: Localidade (vizinhos na rede)
        self.accumulated_stimulus = 0.0

    def update_threshold(self):
        # A5/Adaptation: O threshold dinâmico aumenta com a memória (feedback homeostático negativo)
        # Limiar varia de 0.28 (altamente sensível) a 0.58 (menos sensível)
        return self.base_threshold + (self.memory * 0.30)

    def step_decay(self, decay_rate=0.18):
        # A8: Evolução contínua - a memória decai suavemente no tempo
        self.memory = max(0.0, self.memory - decay_rate)

class ScaleKernelSimulation:
    def __init__(self, num_agents=40, connectivity=4, feedback_enabled=True, noise_level=0.03):
        self.num_agents = num_agents
        self.connectivity = connectivity
        self.feedback_enabled = feedback_enabled
        self.noise_level = noise_level
        self.agents = [Agent(i) for i in range(num_agents)]
        self.setup_ring_lattice()
        self.history = []
        
        # Inicializa alguns agentes ativos de forma aleatória para dar partida
        for _ in range(int(num_agents * 0.15)):
            random.choice(self.agents).active = True

    def setup_ring_lattice(self):
        # A2: Conecta cada agente aos seus vizinhos mais próximos em anel (localidade)
        half_conn = self.connectivity // 2
        for i in range(self.num_agents):
            for step in range(1, half_conn + 1):
                left_neigh = (i - step) % self.num_agents
                right_neigh = (i + step) % self.num_agents
                if left_neigh not in self.agents[i].neighbors:
                    self.agents[i].neighbors.append(left_neigh)
                if right_neigh not in self.agents[i].neighbors:
                    self.agents[i].neighbors.append(right_neigh)

    def run_step(self):
        # A3: Causalidade Distribuída - reseta estímulo acumulado
        for agent in self.agents:
            agent.accumulated_stimulus = 0.0

        # Etapa 1: Propagação Causal (A1, A3)
        for agent in self.agents:
            if agent.active:
                # Agente ativo espalha estímulo aos seus vizinhos locais (A2)
                stimulus_strength = 0.35
                for neighbor_id in agent.neighbors:
                    self.agents[neighbor_id].accumulated_stimulus += stimulus_strength

        # Adiciona ruído estocástico (A8 - Flutuações ambientais/locais)
        for agent in self.agents:
            if random.random() < self.noise_level:
                agent.accumulated_stimulus += 0.20  # pequeno ruído estimulante

        # Etapa 2: Atualização de Estados, Memória e Feedback (A4, A5, A6)
        active_count = 0
        for agent in self.agents:
            # A4: A persistência de informação acumula estímulo recebido de forma mais lenta
            if agent.accumulated_stimulus > 0:
                agent.memory = min(1.0, agent.memory + agent.accumulated_stimulus * 0.3)

            # Define limiar adaptado por feedback (A5)
            current_threshold = agent.update_threshold() if self.feedback_enabled else agent.base_threshold

            # A6: Alternância Dinâmica de Papéis
            if agent.active:
                agent.next_active = False
            else:
                if agent.accumulated_stimulus >= current_threshold:
                    agent.next_active = True
                else:
                    agent.next_active = False

            # Decaimento contínuo da informação para manter fluxo dinâmico (A8)
            agent.step_decay()

        # Etapa 3: Aplicar as transições de estados para o próximo ciclo
        for agent in self.agents:
            agent.active = agent.next_active
            if agent.active:
                active_count += 1

        activity_ratio = active_count / self.num_agents
        
        # Mede entropia informacional (A4/A8)
        entropy = self.calculate_memory_entropy()
        
        return activity_ratio, entropy

    def calculate_memory_entropy(self):
        # Mede quão distribuída está a informação (memória) na rede.
        # Divide a memória em 5 bins (de 0.0 a 1.0)
        bins = [0] * 5
        for agent in self.agents:
            bin_idx = min(4, int(agent.memory * 5))
            bins[bin_idx] += 1
        
        entropy = 0.0
        for count in bins:
            if count > 0:
                p = count / self.num_agents
                entropy -= p * math.log2(p)
        return entropy

    def draw_console(self, step, activity, entropy):
        # Renderização ASCII da rede
        # [*] = Agente Ativo
        # [.] = Agente Inativo (memória limpa)
        # [░], [▒], [▓] = Agente inativo com níveis crescentes de memória (informação armazenada)
        visual = []
        for agent in self.agents:
            if agent.active:
                visual.append("*")
            elif agent.memory > 0.7:
                visual.append("#")
            elif agent.memory > 0.4:
                visual.append("=")
            elif agent.memory > 0.1:
                visual.append("-")
            else:
                visual.append(".")
        
        vis_str = "".join(visual)
        print(f"Passo {step:03d} | Atividade: {activity*100:5.1f}% | Entropia Info: {entropy:4.2f} | Rede: {vis_str}")

def run_simulation(steps=50, feedback=True):
    print("=" * 80)
    print(f"INICIANDO SIMULACAO SCALEKERNEL (Feedback: {'HABILITADO' if feedback else 'DESABILITADO'})")
    print("* = Agente Ativo (Causa)  |  . = Inativo  |  -/-/=/# = Memoria/Informacao Acumulada")
    print("=" * 80)
    
    sim = ScaleKernelSimulation(num_agents=50, connectivity=4, feedback_enabled=feedback)
    
    activities = []
    entropies = []
    
    for step in range(1, steps + 1):
        activity, entropy = sim.run_step()
        sim.draw_console(step, activity, entropy)
        activities.append(activity)
        entropies.append(entropy)
        time.sleep(0.01)  # Pausa curta para efeito visual
        
    avg_activity = sum(activities) / len(activities)
    # Desvio padrão da atividade para medir estabilidade dinâmica
    variance = sum((x - avg_activity) ** 2 for x in activities) / len(activities)
    std_dev = math.sqrt(variance)
    
    print("-" * 80)
    print(f"Metricas Finais (Ciclos 1 a {steps}):")
    print(f" - Atividade Media: {avg_activity*100:.2f}%")
    print(f" - Instabilidade da Atividade (Desvio Padrao): {std_dev*100:.2f}%")
    print(f" - Entropia Informacional Media: {sum(entropies)/len(entropies):.2f}")
    
    # Determinacao de Auto-regulacao Emergente (A7 / A8)
    if avg_activity == 0.0:
        status = "MORTE ESTATICA (Sem atividade)"
    elif avg_activity > 0.8 and std_dev < 0.02:
        status = "SATURACAO TOTAL (Comportamento repetitivo rigido)"
    elif std_dev < 0.15:
        status = "ESTABILIDADE DINAMICA (Auto-regulacao bem sucedida!)"
    else:
        status = "CAOS DESORDENADO (Flutuacoes extremas sem regulacao)"
        
    print(f"Status do Sistema: {status}")
    print("=" * 80)
    return avg_activity, std_dev

if __name__ == "__main__":
    # Roda as duas versões para comparar a diferença que o Feedback dinâmico faz
    run_simulation(steps=40, feedback=True)
    print("\n")
    run_simulation(steps=40, feedback=False)
