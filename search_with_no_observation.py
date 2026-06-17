from collections import deque
import random
import tkinter as tk
from tkinter import ttk


goal = (
    1, 2, 3,
    4, 5, 6,
    7, 8, 0
)

partial_goal = (
    None, None, 3,
    None, None, 4,
    None, None, 5
)

belief_goal_1 = (
    1, 2, 3,
    4, 5, 6,
    7, 8, 0
)

belief_goal_2 = (
    1, 2, 3,
    8, 0, 4,
    7, 6, 5
)

belief_goal_3 = (
    8, 7, 6,
    1, 0, 5,
    2, 3, 4
)

belief_goals = (
    belief_goal_1,
    belief_goal_2,
    belief_goal_3
)

SEARCH_FULL_GOAL = "Belief State - G đầy đủ"
SEARCH_PARTIAL_GOAL = "Không biết S - biết một phần G"
SEARCH_UNKNOWN_START_AND_GOAL = "Không biết S và G - 2 BS, 3 BG"
SEARCH_AND_OR = "AND-OR Graph Search "

moves = {
    "Left": -1,
    "Right": 1,
    "Up": -3,
    "Down": 3
}

opposite_move = {
    "Left": "Right",
    "Right": "Left",
    "Up": "Down",
    "Down": "Up"
}


def goal_test(state):
    return state == goal


def partial_goal_test(state):
    """Check G = [[?, ?, 3], [?, ?, 4], [?, ?, 5]]."""
    return all(
        expected is None or state[index] == expected
        for index, expected in enumerate(partial_goal)
    )


def belief_goals_test(state):
    """Check whether a state is one of BG1, BG2 or BG3."""
    return state in belief_goals


def manhattan_distance(state):
    distance = 0

    for index, value in enumerate(state):
        if value == 0:
            continue

        goal_index = value - 1
        row, column = divmod(index, 3)
        goal_row, goal_column = divmod(goal_index, 3)
        distance += abs(row - goal_row) + abs(column - goal_column)

    return distance


def is_solvable(state):
    values = [value for value in state if value != 0]
    inversions = sum(
        values[i] > values[j]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    )
    return inversions % 2 == 0


def valid_actions(state):
    i = state.index(0)
    actions = []

    if i % 3 != 0:
        actions.append("Left")
    if i % 3 != 2:
        actions.append("Right")
    if i >= 3:
        actions.append("Up")
    if i <= 5:
        actions.append("Down")

    return actions


def swap(state, action):
    state = list(state)
    i_0 = state.index(0)
    new_0 = i_0 + moves[action]
    swapped_tile = state[new_0]

    state[i_0], state[new_0] = state[new_0], state[i_0]

    return tuple(state), swapped_tile


def generate_random_state(steps=20):
    state = goal

    for _ in range(steps):
        action = random.choice(valid_actions(state))
        state, _ = swap(state, action)

    return state


def generate_related_random_state(start, steps=2):
    for _ in range(30):
        state = start

        for _ in range(steps):
            action = random.choice(valid_actions(state))
            state, _ = swap(state, action)

        if state != start:
            return state

    return generate_random_state()


def generate_partial_goal_seed():
    """Create a random solvable state satisfying the partial goal."""
    wildcard_values = [1, 2, 6, 7, 8]

    while True:
        random.shuffle(wildcard_values)
        state = (
            wildcard_values[0], wildcard_values[1], 3,
            wildcard_values[2], wildcard_values[3], 4,
            0, wildcard_values[4], 5
        )

        if is_solvable(state):
            return state


def apply_actions(state, actions):
    current = state

    for action in actions:
        current, _ = swap(current, action)

    return current


def generate_unknown_start_belief():
    """
    Generate BS = {S1, S2} randomly.

    Both states are produced by applying the same random scramble to two
    partial-goal states. Reversing that scramble therefore gives at least one
    guaranteed conformant plan for the unknown real start.
    """
    for _ in range(100):
        goal_state_1 = generate_partial_goal_seed()
        goal_state_2 = generate_partial_goal_seed()

        if goal_state_1 == goal_state_2:
            continue

        states = [goal_state_1, goal_state_2]
        scramble = []
        previous_action = None

        for _ in range(random.randint(3, 7)):
            common_actions = set(valid_actions(states[0]))

            for state in states[1:]:
                common_actions.intersection_update(valid_actions(state))

            if previous_action is not None:
                common_actions.discard(opposite_move[previous_action])

            if not common_actions:
                break

            action = random.choice(sorted(common_actions))
            states = [swap(state, action)[0] for state in states]
            scramble.append(action)
            previous_action = action

        if scramble and not all(partial_goal_test(state) for state in states):
            return states[0], states[1]

    # Guaranteed fallback: the two Right moves disturb the fixed bottom-right 5.
    goal_state_1 = (
        1, 2, 3,
        7, 6, 4,
        0, 8, 5
    )
    goal_state_2 = (
        2, 7, 3,
        1, 6, 4,
        0, 8, 5
    )
    scramble = ["Right", "Right"]
    return (
        apply_actions(goal_state_1, scramble),
        apply_actions(goal_state_2, scramble)
    )


def generate_unknown_start_and_goal_belief():
    """
    Generate BS = {S1, S2} for the unknown-start-and-goal problem.

    Two different states are selected from BG = {BG1, BG2, BG3}, then the
    same random valid action sequence is applied to both. The reverse sequence
    is therefore a guaranteed plan from the generated BS back into BG.
    """
    for _ in range(100):
        selected_goals = random.sample(belief_goals, 2)
        states = list(selected_goals)
        scramble = []
        previous_action = None

        for _ in range(random.randint(3, 7)):
            common_actions = set(valid_actions(states[0]))

            for state in states[1:]:
                common_actions.intersection_update(valid_actions(state))

            if previous_action is not None:
                common_actions.discard(opposite_move[previous_action])

            if not common_actions:
                break

            action = random.choice(sorted(common_actions))
            states = [swap(state, action)[0] for state in states]
            scramble.append(action)
            previous_action = action

        if (
            len(scramble) >= 2
            and states[0] != states[1]
            and not belief_goal_test(states, belief_goals_test)
        ):
            return states[0], states[1]

    # BG2 and BG3 both have the blank in the center, so this is guaranteed.
    fallback_scramble = ["Left", "Up"]
    return (
        apply_actions(belief_goal_2, fallback_scramble),
        apply_actions(belief_goal_3, fallback_scramble)
    )


def generate_and_or_start_state():
    """Generate one state close enough for the recursive AND-OR demonstration."""
    while True:
        state = goal
        previous_action = None

        for _ in range(random.randint(4, 8)):
            actions = valid_actions(state)

            if previous_action is not None:
                reverse = opposite_move[previous_action]
                actions = [action for action in actions if action != reverse]

            action = random.choice(actions)
            state, _ = swap(state, action)
            previous_action = action

        if state != goal:
            return state


def format_state(state):
    return (
        f"[{state[0]} {state[1]} {state[2]}]\n"
        f"[{state[3]} {state[4]} {state[5]}]\n"
        f"[{state[6]} {state[7]} {state[8]}]"
    )


def format_log_state(state):
    return format_state(state).replace("\n", " | ")


def format_belief_state(belief):
    lines = []

    for index, state in enumerate(sorted(belief), start=1):
        lines.append(f"State {index}: {format_log_state(state)}")

    return "\n".join(lines)


def belief_goal_test(belief, state_goal_test=goal_test):
    return all(state_goal_test(state) for state in belief)


def belief_transition(belief, action):
    next_states = []

    for state in belief:
        if action in valid_actions(state):
            next_state, _ = swap(state, action)
        else:
            next_state = state

        next_states.append(next_state)

    return frozenset(next_states)


def project_actions_from_start(start, actions):
    states = [start]
    current = start

    for action in actions:
        if action in valid_actions(current):
            current, _ = swap(current, action)

        states.append(current)

    return states


def Belief_State_BFS(
    start_1,
    start_2,
    max_depth=40,
    max_nodes=200000,
    state_goal_test=goal_test,
    search_name="Belief State BFS"
):
    logs = []
    initial_belief = frozenset([start_1, start_2])

    frontier = deque([(initial_belief, [])])
    explored = {initial_belief}
    expanded_count = 0

    logs.append(f"=== {search_name.upper()} SEARCH LOG ===")
    logs.append("Belief State BFS = dùng BFS trên tập các trạng thái có thể xảy ra.")
    logs.append("Không biết trạng thái thật là S1 hay S2: BS = {S1, S2}.")
    logs.append("Một action được áp dụng cho cả 2 trạng thái.")
    logs.append("Nếu action không hợp lệ với trạng thái nào thì trạng thái đó giữ nguyên.")
    if state_goal_test is partial_goal_test:
        logs.append("G một phần = [[?, ?, 3], [?, ?, 4], [?, ?, 5]].")
        logs.append("Các ô '?' nhận giá trị bất kỳ.")
    elif state_goal_test is belief_goals_test:
        logs.append("Không biết chính xác G, chỉ biết BG = {BG1, BG2, BG3}.")
        logs.append(f"BG1: {format_log_state(belief_goal_1)}")
        logs.append(f"BG2: {format_log_state(belief_goal_2)}")
        logs.append(f"BG3: {format_log_state(belief_goal_3)}")
    else:
        logs.append("G đầy đủ = [[1, 2, 3], [4, 5, 6], [7, 8, 0]].")
    logs.append("Frontier dùng queue: lấy bằng popleft(), thêm bằng append().")
    logs.append(f"max_depth = {max_depth}")
    logs.append("\nInitial Belief State:")
    logs.append(format_belief_state(initial_belief))

    while frontier:
        belief, actions = frontier.popleft()
        expanded_count += 1
        depth = len(actions)

        logs.append("\n--------------------------------")
        logs.append(f"Đang xét Belief State ở depth = {depth}")
        logs.append(f"Số state trong belief = {len(belief)}")
        logs.append(format_belief_state(belief))

        if belief_goal_test(belief, state_goal_test):
            logs.append("=> Tất cả state trong Belief State đều thỏa điều kiện G.")
            states_1 = project_actions_from_start(start_1, actions)
            states_2 = project_actions_from_start(start_2, actions)
            return actions, states_1, states_2, logs

        if depth >= max_depth:
            logs.append("-> Không mở rộng vì đạt max_depth.")
            continue

        if expanded_count >= max_nodes:
            logs.append("=> Dừng vì đạt max_nodes.")
            return "failure"

        for action in moves:
            next_belief = belief_transition(belief, action)

            logs.append(f"\n  Thử action {action}:")
            logs.append("  Belief State mới:")
            logs.append(format_belief_state(next_belief))

            if next_belief in explored:
                logs.append("  -> Bỏ qua: Belief State đã xét.")
                continue

            logs.append("  -> Thêm vào frontier.")
            explored.add(next_belief)
            frontier.append((next_belief, actions + [action]))

    logs.append("\n=> Frontier rỗng, không tìm thấy lời giải Belief State.")
    return "failure"


def searching_with_no_observation(
    start_1,
    start_2,
    max_depth=40,
    max_nodes=200000
):
    """Search with unknown S and partial G = [? ? 3][? ? 4][? ? 5]."""
    return Belief_State_BFS(
        start_1,
        start_2,
        max_depth=max_depth,
        max_nodes=max_nodes,
        state_goal_test=partial_goal_test,
        search_name=SEARCH_PARTIAL_GOAL
    )


def searching_with_unknown_start_and_goal(
    start_1,
    start_2,
    max_depth=40,
    max_nodes=200000
):
    """Search with BS = {S1, S2} and BG = {BG1, BG2, BG3}."""
    return Belief_State_BFS(
        start_1,
        start_2,
        max_depth=max_depth,
        max_nodes=max_nodes,
        state_goal_test=belief_goals_test,
        search_name=SEARCH_UNKNOWN_START_AND_GOAL
    )


def and_or_graph_search(start_state, max_depth=30):
    """
    Return a conditional plan for one initial state.

    An 8-puzzle move is deterministic, so every AND node contains one result
    state. The plan still uses the standard [action, {state: subplan}] form.
    """
    logs = [
        "=== AND-OR GRAPH SEARCH ===",
        "Chỉ có một trạng thái bắt đầu S.",
        "OR node: chọn một action.",
        "AND node: lập kế hoạch cho mọi result state của action.",
        "Trong 8-puzzle, mỗi action hợp lệ có đúng một result state.",
        f"Giới hạn độ sâu tối đa: {max_depth}",
        "",
        "Initial State:",
        format_state(start_state)
    ]

    for depth_limit in range(max_depth + 1):
        logs.append(f"\nThử depth limit = {depth_limit}")
        plan = or_search(start_state, (), depth_limit, logs)

        if plan is not None:
            actions = actions_from_and_or_plan(plan)
            states = project_actions_from_start(start_state, actions)
            logs.append("\n=> Tìm thấy conditional plan.")
            logs.append(f"Actions: {actions}")
            return actions, states, logs, plan

    logs.append("\n=> Không tìm thấy kế hoạch trong giới hạn độ sâu.")
    return "failure"


def or_search(state, path, remaining_depth, logs):
    if goal_test(state):
        return []

    if state in path or remaining_depth == 0:
        return None

    ordered_actions = sorted(
        valid_actions(state),
        key=lambda action: manhattan_distance(swap(state, action)[0])
    )

    for action in ordered_actions:
        result_states = [swap(state, action)[0]]
        plan = and_search(
            result_states,
            path + (state,),
            remaining_depth - 1,
            logs
        )

        if plan is not None:
            logs.append(
                f"OR chọn {action}: {format_log_state(state)}"
            )
            return [action, plan]

    return None


def and_search(states, path, remaining_depth, logs):
    plans = {}

    for state in states:
        plan = or_search(state, path, remaining_depth, logs)

        if plan is None:
            return None

        plans[state] = plan

    return plans


def actions_from_and_or_plan(plan):
    """Extract the action sequence from a single-outcome conditional plan."""
    actions = []
    current_plan = plan

    while current_plan:
        action, branches = current_plan
        actions.append(action)
        current_plan = next(iter(branches.values()))

    return actions


def Belief_State(
    start_1,
    start_2,
    max_depth=40,
    max_nodes=200000,
    state_goal_test=goal_test
):
    return Belief_State_BFS(
        start_1,
        start_2,
        max_depth,
        max_nodes,
        state_goal_test
    )


class BeliefStateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle - Searching with No Observation")

        self.search_type_var = tk.StringVar(value=SEARCH_PARTIAL_GOAL)
        self.state_1, self.state_2 = generate_unknown_start_belief()
        self.steps = []
        self.states_1 = []
        self.states_2 = []
        self.and_or_plan = None
        self.index = 0

        title = tk.Label(
            root,
            text="8 Puzzle - Searching with No Observation",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=10)

        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10)

        board_frame = tk.Frame(main_frame)
        board_frame.grid(row=0, column=0, padx=10, sticky="n")

        boards = tk.Frame(board_frame)
        boards.pack()

        self.board_1_container, self.tiles_1 = self.create_board(
            boards,
            "Possible State S1",
            0
        )
        self.board_2_container, self.tiles_2 = self.create_board(
            boards,
            "Possible State S2",
            1
        )

        control_frame = tk.Frame(board_frame)
        control_frame.pack(pady=10)

        tk.Label(
            control_frame,
            text="Chọn loại tìm kiếm:",
            font=("Arial", 11, "bold")
        ).grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.search_combo = ttk.Combobox(
            control_frame,
            textvariable=self.search_type_var,
            values=[
                SEARCH_PARTIAL_GOAL,
                SEARCH_UNKNOWN_START_AND_GOAL,
                SEARCH_FULL_GOAL,
                SEARCH_AND_OR
            ],
            state="readonly",
            width=32,
            font=("Arial", 11)
        )
        self.search_combo.grid(row=0, column=1, padx=5, pady=5)
        self.search_combo.bind(
            "<<ComboboxSelected>>",
            self.on_search_type_changed
        )

        self.random_button = tk.Button(
            control_frame,
            text="Tạo BS ngẫu nhiên",
            width=16,
            font=("Arial", 11, "bold"),
            command=self.generate_random
        )
        self.random_button.grid(row=1, column=0, padx=5, pady=5)

        self.solve_button = tk.Button(
            control_frame,
            text="Tìm kế hoạch",
            width=18,
            font=("Arial", 11, "bold"),
            command=self.solve
        )
        self.solve_button.grid(row=1, column=1, padx=5, pady=5)

        self.goal_info = tk.Label(
            board_frame,
            text=self.get_goal_description(),
            font=("Consolas", 12, "bold"),
            fg="darkgreen"
        )
        self.goal_info.pack(pady=5)

        self.info = tk.Label(
            board_frame,
            text="BS = {S1, S2}: không biết trạng thái thật là S1 hay S2.",
            font=("Arial", 12),
            fg="blue"
        )
        self.info.pack(pady=5)

        right_frame = tk.Frame(main_frame)
        right_frame.grid(row=0, column=1, padx=10, sticky="n")

        tk.Label(
            right_frame,
            text="Log Searching with No Observation",
            font=("Arial", 14, "bold")
        ).pack()

        self.log_text = tk.Text(
            right_frame,
            width=72,
            height=30,
            font=("Consolas", 9)
        )
        self.log_text.pack()

        result_frame = tk.Frame(root)
        result_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(
            result_frame,
            text="Kết quả",
            font=("Arial", 14, "bold")
        ).pack(anchor="w")

        self.result_text = tk.Text(
            result_frame,
            width=120,
            height=12,
            font=("Consolas", 10)
        )
        self.result_text.pack(fill="x")

        self.draw_boards()

    def create_board(self, parent, title, column):
        container = tk.Frame(parent)
        container.grid(row=0, column=column, padx=12, sticky="n")

        title_label = tk.Label(
            container,
            text=title,
            font=("Arial", 13, "bold")
        )
        title_label.pack(pady=(0, 6))
        container.title_label = title_label

        grid = tk.Frame(container)
        grid.pack()

        tiles = []

        for i in range(9):
            tile = tk.Label(
                grid,
                text="",
                width=5,
                height=2,
                font=("Arial", 26, "bold"),
                borderwidth=2,
                relief="ridge",
                bg="white"
            )
            tile.grid(row=i // 3, column=i % 3, padx=5, pady=5)
            tiles.append(tile)

        return container, tiles

    def draw_board(self, tiles, state):
        for i, value in enumerate(state):
            if value == 0:
                tiles[i].config(text="", bg="lightgray")
            else:
                tiles[i].config(text=str(value), bg="white")

    def draw_boards(self):
        self.draw_board(self.tiles_1, self.state_1)

        if self.search_type_var.get() != SEARCH_AND_OR:
            self.draw_board(self.tiles_2, self.state_2)

    def update_board_visibility(self):
        if self.search_type_var.get() == SEARCH_AND_OR:
            self.board_1_container.title_label.config(text="Initial State S")
            self.board_2_container.grid_remove()
            self.board_1_container.grid_configure(column=0)
        else:
            self.board_1_container.title_label.config(text="Possible State S1")
            self.board_1_container.grid_configure(column=0)
            self.board_2_container.grid()

    def get_selected_goal_test(self):
        if self.search_type_var.get() == SEARCH_AND_OR:
            return goal_test

        if self.search_type_var.get() == SEARCH_PARTIAL_GOAL:
            return partial_goal_test

        if self.search_type_var.get() == SEARCH_UNKNOWN_START_AND_GOAL:
            return belief_goals_test

        return goal_test

    def get_goal_description(self):
        if self.search_type_var.get() == SEARCH_AND_OR:
            return "AND-OR: 1 trạng thái S, G = [1 2 3] [4 5 6] [7 8 0]"

        if self.search_type_var.get() == SEARCH_PARTIAL_GOAL:
            return "G một phần: [? ? 3] [? ? 4] [? ? 5]"

        if self.search_type_var.get() == SEARCH_UNKNOWN_START_AND_GOAL:
            return (
                "BG1: [1 2 3] [4 5 6] [7 8 0]\n"
                "BG2: [1 2 3] [8 0 4] [7 6 5]\n"
                "BG3: [8 7 6] [1 0 5] [2 3 4]"
            )

        return "G đầy đủ: [1 2 3] [4 5 6] [7 8 0]"

    def on_search_type_changed(self, _event=None):
        self.update_board_visibility()
        self.goal_info.config(text=self.get_goal_description())
        self.generate_random()

    def generate_random(self):
        if self.search_type_var.get() == SEARCH_AND_OR:
            self.state_1 = generate_and_or_start_state()
            self.state_2 = self.state_1
        elif self.search_type_var.get() == SEARCH_PARTIAL_GOAL:
            self.state_1, self.state_2 = generate_unknown_start_belief()
        elif self.search_type_var.get() == SEARCH_UNKNOWN_START_AND_GOAL:
            self.state_1, self.state_2 = generate_unknown_start_and_goal_belief()
        else:
            self.state_1 = generate_random_state()
            self.state_2 = generate_related_random_state(self.state_1)

        self.steps = []
        self.states_1 = []
        self.states_2 = []
        self.index = 0

        self.draw_boards()
        self.log_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)
        if self.search_type_var.get() == SEARCH_AND_OR:
            self.info.config(text="Đã tạo một trạng thái S ngẫu nhiên cho AND-OR.")
        else:
            self.info.config(
                text="Đã tạo BS ngẫu nhiên = {S1, S2}. "
                "Trạng thái thật không được quan sát."
            )

    def solve(self):
        self.log_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)

        selected_goal_test = self.get_selected_goal_test()
        and_or_plan = None

        if self.search_type_var.get() == SEARCH_AND_OR:
            and_or_result = and_or_graph_search(self.state_1)

            if and_or_result == "failure":
                result = "failure"
            else:
                actions, states_1, logs, and_or_plan = and_or_result
                result = actions, states_1, [], logs
        elif selected_goal_test is partial_goal_test:
            result = searching_with_no_observation(
                self.state_1,
                self.state_2
            )
        elif selected_goal_test is belief_goals_test:
            result = searching_with_unknown_start_and_goal(
                self.state_1,
                self.state_2
            )
        else:
            result = Belief_State_BFS(
                self.state_1,
                self.state_2,
                state_goal_test=selected_goal_test,
                search_name=self.search_type_var.get()
            )

        if result == "failure":
            if self.search_type_var.get() == SEARCH_AND_OR:
                self.info.config(text="Không tìm thấy AND-OR plan từ S tới G.")
            else:
                self.info.config(
                    text="Không tìm thấy kế hoạch chung cho BS = {S1, S2}."
                )
            return

        self.steps, self.states_1, self.states_2, logs = result
        self.and_or_plan = and_or_plan
        self.index = 0

        self.log_text.insert(tk.END, "\n".join(logs))
        self.log_text.insert(tk.END, "\n\n=== SOLUTION PATH ANIMATION ===\n\n")
        self.log_text.see(tk.END)

        self.show_result_path()

        self.random_button.config(state="disabled")
        self.solve_button.config(state="disabled")
        self.search_combo.config(state="disabled")
        self.show_step()

    def show_result_path(self):
        self.result_text.insert(
            tk.END,
            f"Loại: {self.search_type_var.get()}\n"
        )
        self.result_text.insert(tk.END, f"{self.get_goal_description()}\n")
        if self.search_type_var.get() == SEARCH_AND_OR:
            step_label = "Tổng số bước"
        else:
            step_label = "Tổng số bước đi chung"

        self.result_text.insert(tk.END, f"{step_label}: {len(self.steps)}\n")

        if self.search_type_var.get() == SEARCH_AND_OR:
            self.result_text.insert(tk.END, "\nTrạng thái ban đầu S:\n")
            self.result_text.insert(tk.END, format_state(self.states_1[0]))
            self.result_text.insert(tk.END, "\n\n")

            for i in range(1, len(self.states_1)):
                self.result_text.insert(
                    tk.END,
                    f"Step {i}: {self.steps[i - 1]}\n"
                )
                self.result_text.insert(tk.END, format_state(self.states_1[i]))
                self.result_text.insert(tk.END, "\n\n")

            self.result_text.insert(
                tk.END,
                f"Conditional plan: {self.and_or_plan}\n"
            )

            if goal_test(self.states_1[-1]):
                self.result_text.insert(tk.END, "Trạng thái S đã tới G.\n")
            else:
                self.result_text.insert(tk.END, "Trạng thái S chưa tới G.\n")

            return

        self.result_text.insert(tk.END, "\nTrạng thái ban đầu 1:\n")
        self.result_text.insert(tk.END, format_state(self.states_1[0]))
        self.result_text.insert(tk.END, "\n")

        self.result_text.insert(tk.END, "\nTrạng thái ban đầu 2:\n")
        self.result_text.insert(tk.END, format_state(self.states_2[0]))
        self.result_text.insert(tk.END, "\n\n")

        for i in range(1, len(self.states_1)):
            self.result_text.insert(tk.END, f"Step {i}: {self.steps[i - 1]}\n")

            self.result_text.insert(tk.END, "State 1:\n")
            self.result_text.insert(tk.END, format_state(self.states_1[i]))
            self.result_text.insert(tk.END, "\n\n")

            self.result_text.insert(tk.END, "State 2:\n")
            self.result_text.insert(tk.END, format_state(self.states_2[i]))
            self.result_text.insert(tk.END, "\n\n")

        selected_goal_test = self.get_selected_goal_test()

        if (
            selected_goal_test(self.states_1[-1])
            and selected_goal_test(self.states_2[-1])
        ):
            self.result_text.insert(tk.END, "Cả S1 và S2 đều thỏa điều kiện G.\n")
        else:
            self.result_text.insert(tk.END, "BS chưa thỏa điều kiện G.\n")

    def show_step(self):
        if self.index < len(self.states_1):
            self.state_1 = self.states_1[self.index]

            if self.search_type_var.get() != SEARCH_AND_OR:
                self.state_2 = self.states_2[self.index]

            self.draw_boards()

            if self.index == 0:
                if self.search_type_var.get() == SEARCH_AND_OR:
                    self.info.config(
                        text=f"Initial State S | Total moves: {len(self.steps)}"
                    )
                    self.log_text.insert(
                        tk.END,
                        "Step 0 Solution: Initial State S\n"
                        f"{format_state(self.state_1)}\n\n"
                    )
                else:
                    self.info.config(
                        text=f"Initial Belief State | Total moves: {len(self.steps)}"
                    )
                    self.log_text.insert(
                        tk.END,
                        "Step 0 Solution: Initial Belief State\n"
                        f"State 1:\n{format_state(self.state_1)}\n\n"
                        f"State 2:\n{format_state(self.state_2)}\n\n"
                    )
            else:
                move = self.steps[self.index - 1]
                previous_1 = self.states_1[self.index - 1]

                self.info.config(
                    text=f"Step {self.index}/{len(self.steps)} | Action chung: {move}"
                )

                if self.search_type_var.get() == SEARCH_AND_OR:
                    self.log_text.insert(
                        tk.END,
                        f"Step {self.index} Solution: Action {move}\n"
                        f"{self.describe_transition(previous_1, self.state_1, move)}"
                        f"{format_state(self.state_1)}\n\n"
                    )
                else:
                    previous_2 = self.states_2[self.index - 1]
                    self.log_text.insert(
                        tk.END,
                        f"Step {self.index} Solution: Action {move}\n"
                        "State 1:\n"
                        f"{self.describe_transition(previous_1, self.state_1, move)}"
                        f"{format_state(self.state_1)}\n"
                        "\n"
                        "State 2:\n"
                        f"{self.describe_transition(previous_2, self.state_2, move)}"
                        f"{format_state(self.state_2)}\n"
                        "\n"
                    )

            self.log_text.see(tk.END)
            self.index += 1
            self.root.after(700, self.show_step)
        else:
            self.random_button.config(state="normal")
            self.solve_button.config(state="normal")
            self.search_combo.config(state="readonly")

            selected_goal_test = self.get_selected_goal_test()

            if self.search_type_var.get() == SEARCH_AND_OR:
                success = selected_goal_test(self.state_1)
            else:
                success = (
                    selected_goal_test(self.state_1)
                    and selected_goal_test(self.state_2)
                )

            if success:
                if self.search_type_var.get() == SEARCH_AND_OR:
                    self.info.config(text="Thành công: trạng thái S đã tới G!")
                else:
                    self.info.config(text="Thành công: mọi state trong BS đều thỏa G!")
            else:
                if self.search_type_var.get() == SEARCH_AND_OR:
                    self.info.config(text="Trạng thái S chưa tới G.")
                else:
                    self.info.config(text="Belief State chưa thỏa điều kiện G.")

    def describe_transition(self, previous_state, current_state, action):
        if action not in valid_actions(previous_state):
            return "Action không hợp lệ, trạng thái giữ nguyên.\n"

        new_zero = current_state.index(0)
        swapped_tile = previous_state[new_zero]
        return f"Hoán đổi 0 với {swapped_tile}\n"


if __name__ == "__main__":
    root = tk.Tk()
    app = BeliefStateApp(root)
    root.mainloop()
