from collections import deque
import tkinter as tk
from tkinter import ttk
import random
import heapq
import math

goal = (
    1, 2, 3,
    4, 5, 6,
    7, 8, 0
)

moves = {
    "Left": -1,
    "Right": 1,
    "Up": -3,
    "Down": 3
}

# ===================== CSP ALGORITHMS =====================
#
# Trong 8-puzzle, bài toán CSP được mô hình hóa như sau:
#   - Biến (Variables): 9 ô, mỗi ô là X0..X8
#   - Miền giá trị (Domain): {0,1,2,3,4,5,6,7,8}
#   - Ràng buộc (Constraints): mỗi ô có giá trị khác nhau (all-different)
#     và kết quả xếp đặt khớp với goal state.
# Trạng thái đích: goal = (1,2,3,4,5,6,7,8,0)
# ----------------------------------------------------------------


# ===================== MIN-CONFLICTS =====================
# function MIN-CONFLICTS(csp, max_steps) returns a solution or failure
#   current <- an initial complete assignment for csp
#   for i = 1 to max_steps do
#       if current is a solution for csp then return current
#       var <- a randomly chosen conflicted variable from csp.VARIABLES
#       value <- the value v for var that minimizes CONFLICTS(var,v,current,csp)
#       set var <- value in current
#   return failure

def _count_conflicts_mc(state):
    """Đếm số vị trí bị xung đột (ô không đúng chỗ) trong 8-puzzle."""
    return sum(
        1
        for i in range(9)
        if state[i] is not None and state[i] != 0 and state[i] != goal[i]
    )


def _assignment_to_partial_state(assignment):
    """Tạo state CSP đang gán dở; ô chưa gán để trống thay vì lấy từ initial_state."""
    return tuple(assignment.get(i, None) for i in range(9))


def _conflicts_for_var(position, value, state):
    """
    Đếm số xung đột nếu đặt 'value' vào 'position'.
    Xung đột = giá trị khác với goal tại vị trí đó (ngoại trừ ô trống).
    """
    conflict = 0
    if value != 0 and value != goal[position]:
        conflict += 1
    # Kiểm tra ô nào đang giữ value bị đẩy đi
    for i in range(9):
        if i != position and state[i] == value:
            if value != 0 and value != goal[i]:
                conflict += 1
    return conflict


def min_conflicts_8puzzle(initial_state, max_steps=1000):
    """
    MIN-CONFLICTS cho 8-puzzle.
    Khởi tạo bằng trạng thái ban đầu, mỗi bước chọn ngẫu nhiên
    một biến bị xung đột rồi gán giá trị giảm xung đột nhất.
    """
    logs = []
    logs.append("=== MIN-CONFLICTS SEARCH LOG ===")
    logs.append(f"max_steps = {max_steps}")
    logs.append("Mô hình CSP:")
    logs.append("  Variables: X0..X8 (9 ô)")
    logs.append("  Domain: {0,1,2,3,4,5,6,7,8} (mỗi biến)")
    logs.append("  Constraints: all-different + khớp goal")
    logs.append(f"Initial State: {initial_state}")

    # current = trạng thái ban đầu (đã là gán đầy đủ)
    current = list(initial_state)

    # Tạo node gốc để theo dõi đường đi
    root_node = Node(tuple(current))
    path_nodes = [root_node]   # danh sách node theo bước

    for i in range(1, max_steps + 1):
        state_tuple = tuple(current)

        logs.append(f"\n--- Bước {i} ---")
        logs.append(f"current = {state_tuple}")
        conflicts_now = _count_conflicts_mc(state_tuple)
        logs.append(f"Số ô xung đột = {conflicts_now}")

        # Kiểm tra goal
        if state_tuple == goal:
            logs.append("=> Tìm thấy trạng thái đích!")
            # Xây dựng chuỗi node
            steps_out, states_out, costs_out = [], [], []
            for nd in path_nodes:
                states_out.append(nd.state)
                costs_out.append(0)
            for j in range(1, len(path_nodes)):
                steps_out.append("Min-Conflicts Move")
            return steps_out, states_out, costs_out, logs

        # Chọn ngẫu nhiên một biến bị xung đột
        conflicted = [pos for pos in range(9)
                      if current[pos] != 0 and current[pos] != goal[pos]]
        if not conflicted:
            # Chỉ ô trống bị sai, hoán đổi trực tiếp
            conflicted = [pos for pos in range(9) if current[pos] != goal[pos]]

        var = random.choice(conflicted)
        logs.append(f"var (ô xung đột được chọn) = vị trí {var}, giá trị = {current[var]}")

        # Tìm giá trị giảm xung đột nhất trong domain (0..8)
        # Domain còn lại = các giá trị chưa dùng + giá trị hiện tại
        used = set(current)
        domain = list(range(9))
        best_value = current[var]
        best_conflict = float('inf')

        for v in domain:
            # Thử gán v vào var
            old_val = current[var]
            # Tìm vị trí đang chứa v (nếu có)
            other_pos = None
            for k in range(9):
                if k != var and current[k] == v:
                    other_pos = k
                    break
            if other_pos is not None:
                current[var], current[other_pos] = v, old_val
                c = _count_conflicts_mc(tuple(current))
                current[var], current[other_pos] = old_val, v
            else:
                current[var] = v
                c = _count_conflicts_mc(tuple(current))
                current[var] = old_val

            logs.append(f"  Thử value = {v} => conflicts = {c}")
            if c < best_conflict:
                best_conflict = c
                best_value = v

        logs.append(f"=> Chọn value = {best_value} (conflicts = {best_conflict})")

        # Thực hiện gán: hoán đổi nếu cần
        old_val = current[var]
        if best_value != old_val:
            other_pos = None
            for k in range(9):
                if k != var and current[k] == best_value:
                    other_pos = k
                    break
            if other_pos is not None:
                current[var], current[other_pos] = best_value, old_val
            else:
                current[var] = best_value

        new_node = Node(
            state=tuple(current),
            parent=path_nodes[-1],
            action="Min-Conflicts Move",
            step=i,
            cost=0
        )
        path_nodes.append(new_node)

    logs.append("\n=> Đã hết max_steps, không tìm được lời giải.")
    logs.append("=> MIN-CONFLICTS thất bại.")
    return "failure", [], [], logs


# ===================== BACKTRACKING =====================
# function BACKTRACKING-SEARCH(csp) returns a solution, or failure
#   return RECURSIVE-BACKTRACKING({}, csp)
#
# function RECURSIVE-BACKTRACKING(assignment, csp)
#   if assignment is complete then return assignment
#   var <- SELECT-UNASSIGNED-VARIABLE(Variables[csp], assignment, csp)
#   for each value in ORDER-DOMAIN-VALUES(var, assignment, csp) do
#       if value is consistent with assignment according to Constraints[csp] then
#           add {var=value} to assignment
#           result <- RECURSIVE-BACKTRACKING(assignment, csp)
#           if result != failure then return result
#           remove {var=value} from assignment
#   return failure

def _is_consistent_bt(assignment, var, value):
    """
    Kiểm tra gán var=value có nhất quán không:
    - Không trùng giá trị với biến đã gán (all-different)
    """
    for assigned_var, assigned_val in assignment.items():
        if assigned_val == value:
            return False
    return True


def _recursive_backtracking(assignment, variables, logs, call_count, states_out, steps_out):
    """Hàm đệ quy RECURSIVE-BACKTRACKING."""
    call_count[0] += 1
    depth = len(assignment)
    indent = "  " * depth

    # Kiểm tra gán đầy đủ
    if len(assignment) == 9:
        # Tạo state từ assignment
        state = tuple(assignment[i] for i in range(9))
        logs.append(f"{indent}=> Assignment đầy đủ: {state}")
        if state == goal:
            logs.append(f"{indent}=> Đây là GOAL STATE!")
            return assignment
        else:
            logs.append(f"{indent}=> Không phải goal, backtrack.")
            return None

    # SELECT-UNASSIGNED-VARIABLE: chọn biến chưa gán theo thứ tự
    var = None
    for v in variables:
        if v not in assignment:
            var = v
            break

    logs.append(f"{indent}Chọn biến X{var} (vị trí {var})")
    logs.append(f"{indent}Goal yêu cầu giá trị = {goal[var]}")

    # ORDER-DOMAIN-VALUES: ưu tiên goal[var] trước
    domain = list(range(9))
    domain.sort(key=lambda v: (0 if v == goal[var] else 1))

    for value in domain:
        logs.append(f"{indent}  Thử X{var} = {value}")

        if _is_consistent_bt(assignment, var, value):
            logs.append(f"{indent}  => Nhất quán, thêm vào assignment")
            assignment[var] = value

            # --- Ghi nhận trạng thái cho animation ---
            states_out.append(_assignment_to_partial_state(assignment))
            steps_out.append(f"Assign X{var}={value}")

            result = _recursive_backtracking(assignment, variables, logs, call_count, states_out, steps_out)

            if result is not None:
                return result

            logs.append(f"{indent}  => Backtrack: X{var} = {value} không dẫn đến goal")
            del assignment[var]

            # --- Ghi nhận trạng thái backtrack cho animation ---
            states_out.append(_assignment_to_partial_state(assignment))
            steps_out.append(f"Backtrack X{var}")
        else:
            logs.append(f"{indent}  => Không nhất quán (trùng giá trị), bỏ qua")

    return None


def backtracking_8puzzle(initial_state):
    """
    BACKTRACKING-SEARCH cho 8-puzzle.
    Xây dựng lại goal state từ đầu bằng backtracking trên CSP.
    """
    logs = []
    logs.append("=== BACKTRACKING SEARCH LOG ===")
    logs.append("Mô hình CSP:")
    logs.append("  Variables: X0..X8 (9 ô)")
    logs.append("  Domain: {0,1,2,3,4,5,6,7,8} (mỗi biến)")
    logs.append("  Constraints: all-different + kết quả = goal")
    logs.append(f"  Goal: {goal}")
    logs.append(f"Initial State (start): {initial_state}")
    logs.append("")
    logs.append("Bắt đầu RECURSIVE-BACKTRACKING({}, csp):")

    variables = list(range(9))
    assignment = {}
    call_count = [0]

    states_out = [initial_state]
    steps_out = []

    result = _recursive_backtracking(assignment, variables, logs, call_count, states_out, steps_out)

    logs.append(f"\nTổng số lần gọi đệ quy: {call_count[0]}")

    if result is not None:
        state_solution = tuple(result[i] for i in range(9))
        logs.append(f"\n=> Tìm được assignment: {state_solution}")

        costs_out = [0] * len(states_out)
        return steps_out, states_out, costs_out, logs
    else:
        logs.append("=> BACKTRACKING thất bại.")
        return "failure", [], [], logs


# ===================== FORWARD CHECKING =====================
# function FORWARD-CHECKING-SEARCH(csp) returns a solution, or failure
#   return FORWARD-CHECK({}, csp)
#
# function FORWARD-CHECK(assignment, csp)
#   if assignment is complete then return assignment
#   var <- SELECT-UNASSIGNED-VARIABLE(csp)
#   for each value in ORDER-DOMAIN-VALUES(var, assignment, csp) do
#       if value is consistent with assignment then
#           add {var=value} to assignment
#           removed <- FORWARD-CHECKING(csp, var, value)
#           if removed != failure then
#               result <- FORWARD-CHECK(assignment, csp)
#               if result != failure then return result
#           restore removed values to domains
#           remove {var=value} from assignment
#   return failure

def _forward_checking_prune(domains, var, value, assignment):
    """
    FORWARD-CHECKING: loại bỏ value đã dùng khỏi domain các biến chưa gán.
    Trả về dict {neighbor: [removed_values]} hoặc None nếu domain rỗng.
    """
    removed = {}
    for other_var in range(9):
        if other_var != var and other_var not in assignment:
            if value in domains[other_var]:
                if other_var not in removed:
                    removed[other_var] = []
                removed[other_var].append(value)
                domains[other_var].remove(value)
                if len(domains[other_var]) == 0:
                    return None  # Domain rỗng -> failure
    return removed


def _forward_check_recursive(assignment, domains, variables, logs, call_count, states_out, steps_out):
    """Hàm đệ quy FORWARD-CHECK."""
    call_count[0] += 1
    depth = len(assignment)
    indent = "  " * depth

    if len(assignment) == 9:
        state = tuple(assignment[i] for i in range(9))
        logs.append(f"{indent}=> Assignment đầy đủ: {state}")
        if state == goal:
            logs.append(f"{indent}=> GOAL STATE!")
            return assignment
        else:
            logs.append(f"{indent}=> Không phải goal, backtrack.")
            return None

    # SELECT-UNASSIGNED-VARIABLE (MRV: chọn biến có domain nhỏ nhất)
    var = min(
        [v for v in variables if v not in assignment],
        key=lambda v: len(domains[v])
    )
    logs.append(f"{indent}Chọn biến X{var} | Domain = {sorted(domains[var])} | Goal yêu cầu = {goal[var]}")

    # ORDER-DOMAIN-VALUES: ưu tiên goal[var]
    ordered_vals = sorted(domains[var], key=lambda v: (0 if v == goal[var] else 1))

    for value in ordered_vals:
        logs.append(f"{indent}  Thử X{var} = {value}")

        # Kiểm tra nhất quán
        consistent = all(assignment[av] != value for av in assignment)
        if not consistent:
            logs.append(f"{indent}  => Không nhất quán, bỏ qua")
            continue

        logs.append(f"{indent}  => Nhất quán, thêm vào assignment")
        assignment[var] = value

        # --- Ghi nhận trạng thái cho animation ---
        states_out.append(_assignment_to_partial_state(assignment))
        steps_out.append(f"Assign X{var}={value}")

        domains_copy = {k: list(v) for k, v in domains.items()}

        # FORWARD-CHECKING: cập nhật domain
        removed = _forward_checking_prune(domains, var, value, assignment)

        if removed is not None:
            domain_info = {k: sorted(domains[k]) for k in range(9) if k not in assignment}
            logs.append(f"{indent}  Domain sau FC: {domain_info}")

            result = _forward_check_recursive(assignment, domains, variables, logs, call_count, states_out, steps_out)
            if result is not None:
                return result
        else:
            logs.append(f"{indent}  => FC phát hiện domain rỗng, cắt nhánh")

        # Khôi phục domain
        for k, v in domains_copy.items():
            domains[k] = v

        logs.append(f"{indent}  => Backtrack: X{var} = {value}")
        del assignment[var]

        # --- Ghi nhận trạng thái backtrack cho animation ---
        states_out.append(_assignment_to_partial_state(assignment))
        steps_out.append(f"Backtrack X{var}")

    return None


def forward_checking_8puzzle(initial_state):
    """
    FORWARD-CHECKING-SEARCH cho 8-puzzle.
    """
    logs = []
    logs.append("=== FORWARD CHECKING SEARCH LOG ===")
    logs.append("Mô hình CSP:")
    logs.append("  Variables: X0..X8 (9 ô)")
    logs.append("  Domain ban đầu: {0,1,2,3,4,5,6,7,8} mỗi biến")
    logs.append("  Constraints: all-different + kết quả = goal")
    logs.append(f"  Goal: {goal}")
    logs.append(f"Initial State: {initial_state}")
    logs.append("")
    logs.append("Bắt đầu FORWARD-CHECK({}, csp):")

    variables = list(range(9))
    domains = {i: list(range(9)) for i in range(9)}
    assignment = {}
    call_count = [0]

    states_out = [initial_state]
    steps_out = []

    result = _forward_check_recursive(assignment, domains, variables, logs, call_count, states_out, steps_out)

    logs.append(f"\nTổng số lần gọi đệ quy: {call_count[0]}")

    if result is not None:
        state_solution = tuple(result[i] for i in range(9))
        logs.append(f"\n=> Tìm được assignment: {state_solution}")

        costs_out = [0] * len(states_out)
        return steps_out, states_out, costs_out, logs
    else:
        logs.append("=> FORWARD CHECKING thất bại.")
        return "failure", [], [], logs


# ===================== AC-3 =====================
# function AC-3(csp) returns the CSP, possibly with reduced domains
#   queue <- all arcs in csp
#   while queue is not empty do
#       (Xi, Xj) <- REMOVE-FIRST(queue)
#       if RM-INCONSISTENT-VALUES(Xi, Xj) then
#           for each Xk in NEIGHBORS[Xi] do
#               add (Xk, Xi) to queue
#   return csp
#
# function RM-INCONSISTENT-VALUES(Xi, Xj)
#   removed <- false
#   for each x in DOMAIN[Xi] do
#       if no value y in DOMAIN[Xj] allows (x,y) to satisfy constraint(Xi,Xj)
#       then delete x from DOMAIN[Xi]; removed <- true
#   return removed

def _rm_inconsistent_values(domains, xi, xj, logs):
    """
    RM-INCONSISTENT-VALUES cho ràng buộc all-different (Xi != Xj).
    Loại x khỏi domain[Xi] nếu không tồn tại y trong domain[Xj] mà x != y.
    """
    removed = False
    to_remove = []

    for x in list(domains[xi]):
        # Kiểm tra có y trong domain[Xj] thỏa x != y không
        satisfiable = any(y != x for y in domains[xj])
        if not satisfiable:
            to_remove.append(x)
            removed = True

    for x in to_remove:
        domains[xi].remove(x)
        logs.append(f"  RM-INCONSISTENT: Loại {x} khỏi domain[X{xi}] (do X{xj} không có giá trị khác)")

    return removed


def ac3_8puzzle(initial_state):
    """
    AC-3 cho 8-puzzle (mô hình CSP all-different).
    """
    logs = []
    logs.append("=== AC-3 SEARCH LOG ===")
    logs.append("Mô hình CSP:")
    logs.append("  Variables: X0..X8 (9 ô)")
    logs.append("  Domain ban đầu: {0,1,2,3,4,5,6,7,8} mỗi biến")
    logs.append("  Constraints: all-different + unary goal Xi = goal[i]")
    logs.append(f"  Goal: {goal}")
    logs.append(f"Initial State: {initial_state}")
    logs.append("")

    variables = list(range(9))
    domains = {i: list(range(9)) for i in range(9)}

    # Bước 1: áp dụng ràng buộc unary goal trước khi chạy AC-3.
    logs.append("Bước 1: Áp dụng ràng buộc goal vào domain")
    logs.append("  initial_state chỉ là trạng thái bắt đầu animation; domain CSP lấy từ goal.")
    for pos, val in enumerate(goal):
        domains[pos] = [val]
        logs.append(f"  X{pos} phải bằng {val} => domain = [{val}]")

    # Bước 2: Chạy AC-3
    logs.append("\nBước 2: Chạy AC-3")
    # Khởi tạo queue: tất cả các cặp cung (Xi, Xj) với i != j
    queue = deque()
    for i in variables:
        for j in variables:
            if i != j:
                queue.append((i, j))

    logs.append(f"Queue ban đầu: {len(queue)} cung")
    arc_count = 0

    while queue:
        xi, xj = queue.popleft()
        arc_count += 1
        logs.append(f"\n[Cung {arc_count}] Xét (X{xi}, X{xj})")
        logs.append(f"  domain[X{xi}] = {domains[xi]}")
        logs.append(f"  domain[X{xj}] = {domains[xj]}")

        if _rm_inconsistent_values(domains, xi, xj, logs):
            if len(domains[xi]) == 0:
                logs.append(f"  => domain[X{xi}] rỗng! AC-3 phát hiện bất nhất quán.")
                logs.append("=> AC-3 THẤT BẠI")
                return "failure", [], [], logs

            # Thêm tất cả (Xk, Xi) với Xk là neighbor của Xi
            for xk in variables:
                if xk != xi and xk != xj:
                    queue.append((xk, xi))
                    logs.append(f"  Thêm (X{xk}, X{xi}) vào queue")

    logs.append(f"\nAC-3 hoàn tất sau {arc_count} cung.")
    logs.append("Domain sau AC-3:")
    for i in variables:
        logs.append(f"  X{i}: {domains[i]}")

    # Bước 3: Tạo assignment từ domain singleton sau AC-3.
    if any(len(domains[i]) != 1 for i in variables):
        logs.append("=> Không thể xác định assignment từ domain.")
        return "failure", [], [], logs

    state_solution = tuple(domains[i][0] for i in variables)
    logs.append(f"\nKết quả AC-3: {state_solution}")

    if state_solution != goal:
        logs.append("=> Domain sau AC-3 không khớp goal.")
        return "failure", [], [], logs

    logs.append("=> AC-3 hoàn thành: mọi domain là singleton và khớp goal.")

    assignment = {}
    states_out = [initial_state]
    steps_out = []

    for var in variables:
        value = domains[var][0]
        assignment[var] = value
        states_out.append(_assignment_to_partial_state(assignment))
        steps_out.append(f"AC-3 set X{var}={value}")

    costs_out = [0] * len(states_out)
    return steps_out, states_out, costs_out, logs

class Node:
    def __init__(self, state, parent=None, action=None, step=0, cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.step = step
        self.cost = cost


def goal_test(state):
    return state == goal


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


def misplaced_tiles(state):
    count = 0
    for i in range(9):
        if state[i] != 0 and state[i] != goal[i]:
            count += 1
    return count

def inversion_count(state):
    arr = [x for x in state if x != 0]
    count = 0

    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]:
                count += 1

    return count
def manhattan_distance(state):
    distance = 0

    for i in range(9):
        value = state[i]

        if value != 0:
            current_row = i // 3
            current_col = i % 3

            goal_index = goal.index(value)
            goal_row = goal_index // 3
            goal_col = goal_index % 3

            distance += abs(current_row - goal_row) + abs(current_col - goal_col)

    return distance

def child_node(node, action, use_cost=False):
    new_state, _ = swap(node.state, action)

    if use_cost:
        step_cost = misplaced_tiles(new_state)
        new_cost = node.cost + step_cost
    else:
        new_cost = node.cost

    return Node(
        state=new_state,
        parent=node,
        action=action,
        step=node.step + 1,
        cost=new_cost
    )


def solution(node):
    steps = []
    states = []
    costs = []

    while node is not None:
        states.append(node.state)
        costs.append(node.cost)

        if node.action is not None:
            steps.append(node.action)

        node = node.parent

    states.reverse()
    steps.reverse()
    costs.reverse()

    return steps, states, costs


def format_state(state):
    cells = ["." if value is None else value for value in state]
    return (
        f"[{cells[0]} {cells[1]} {cells[2]}]\n"
        f"[{cells[3]} {cells[4]} {cells[5]}]\n"
        f"[{cells[6]} {cells[7]} {cells[8]}]"
    )


def format_log_state(state):
    return format_state(state).replace("\n", " | ")


# ===================== BFS =====================

def bfs(initial_state):
    logs = []
    node = Node(initial_state)

    frontier = deque([node])
    frontier_states = {node.state}
    explored = set()

    logs.append("=== BFS SEARCH LOG ===")
    logs.append(f"Initial State: {format_log_state(initial_state)}")

    while frontier:
        node = frontier.popleft()
        frontier_states.remove(node.state)

        logs.append("\n--------------------------------")
        logs.append(f"Đang xét node ở step = {node.step}")
        logs.append(format_state(node.state))

        if goal_test(node.state):
            logs.append("=> Tìm thấy trạng thái đích!")
            steps, states, costs = solution(node)
            return steps, states, costs, logs

        explored.add(node.state)

        for action in valid_actions(node.state):
            child = child_node(node, action)

            new_zero = child.state.index(0)
            swapped_tile = node.state[new_zero]

            logs.append(f"\n  Thử move {action}:")
            logs.append(f"  Hoán đổi 0 với {swapped_tile}")
            logs.append(f"  Trạng thái tạo ra: {format_log_state(child.state)}")

            if child.state in explored:
                logs.append("  -> Bỏ qua: đã xét.")
            elif child.state in frontier_states:
                logs.append("  -> Bỏ qua: đã có trong frontier.")
            else:
                logs.append("  -> Thêm vào frontier.")
                frontier.append(child)
                frontier_states.add(child.state)

    return None


# ===================== DFS =====================

def dfs(initial_state):
    logs = []
    node = Node(initial_state)

    frontier = [node]
    frontier_states = {node.state}
    explored = set()

    logs.append("=== DFS SEARCH LOG ===")
    logs.append(f"Initial State: {format_log_state(initial_state)}")

    while frontier:
        node = frontier.pop()
        frontier_states.remove(node.state)

        logs.append("\n--------------------------------")
        logs.append(f"Đang xét node ở step = {node.step}")
        logs.append(format_state(node.state))

        if goal_test(node.state):
            logs.append("=> Tìm thấy trạng thái đích!")
            steps, states, costs = solution(node)
            return steps, states, costs, logs

        explored.add(node.state)

        for action in reversed(valid_actions(node.state)):
            child = child_node(node, action)

            new_zero = child.state.index(0)
            swapped_tile = node.state[new_zero]

            logs.append(f"\n  Thử move {action}:")
            logs.append(f"  Hoán đổi 0 với {swapped_tile}")
            logs.append(f"  Trạng thái tạo ra: {format_log_state(child.state)}")

            if child.state in explored:
                logs.append("  -> Bỏ qua: đã xét.")
            elif child.state in frontier_states:
                logs.append("  -> Bỏ qua: đã có trong stack.")
            else:
                logs.append("  -> Thêm vào stack.")
                frontier.append(child)
                frontier_states.add(child.state)

    return None


# ===================== UCS =====================

def ucs(initial_state):
    logs = []

    # Cost ban đầu = 0
    node = Node(
        state=initial_state,
        cost=0
    )

    frontier = []
    counter = 0

    heapq.heappush(frontier, (node.cost, counter, node))

    frontier_costs = {
        node.state: node.cost
    }

    explored = set()

    logs.append("=== UCS SEARCH LOG ===")
    logs.append(f"Initial State: {format_log_state(initial_state)}")
    logs.append("Cost ban đầu = 0")

    while frontier:
        current_cost, _, node = heapq.heappop(frontier)

        if node.state in explored:
            continue

        logs.append("\n--------------------------------")
        logs.append(f"Đang xét node ở step = {node.step}")
        logs.append(format_state(node.state))
        logs.append(f"Tổng cost hiện tại = {node.cost}")
        logs.append(f"Số ô khác goal = {misplaced_tiles(node.state)}")

        if goal_test(node.state):
            logs.append("=> Tìm thấy trạng thái đích!")
            steps, states, costs = solution(node)
            return steps, states, costs, logs

        explored.add(node.state)

        for action in valid_actions(node.state):
            child = child_node(node, action, use_cost=True)

            new_zero = child.state.index(0)
            swapped_tile = node.state[new_zero]
            state_cost = misplaced_tiles(child.state)

            logs.append(f"\n  Thử move {action}:")
            logs.append(f"  Hoán đổi 0 với {swapped_tile}")
            logs.append(f"  Trạng thái tạo ra: {format_log_state(child.state)}")
            logs.append(f"  Cost trạng thái này = {state_cost}")
            logs.append(f"  Tổng cost mới = {child.cost}")

            if child.state in explored:
                logs.append("  -> Bỏ qua: đã xét.")

            elif child.state not in frontier_costs or child.cost < frontier_costs[child.state]:
                counter += 1
                heapq.heappush(frontier, (child.cost, counter, child))
                frontier_costs[child.state] = child.cost
                logs.append("  -> Thêm vào priority queue.")

            else:
                logs.append("  -> Bỏ qua: cost không tốt hơn.")

    return None


# ===================== IDS =====================

def depth(node):
    return node.step


def is_cycle(node):
    current = node.parent

    while current is not None:
        if current.state == node.state:
            return True
        current = current.parent

    return False


def depth_limited_search(initial_state, limit):
    logs = []
    node = Node(initial_state)
    frontier = [node]

    logs.append(f"=== IDS LIMIT = {limit} ===")

    result = "failure"

    while frontier:
        node = frontier.pop()

        logs.append("\n--------------------------------")
        logs.append(f"Đang xét node ở depth = {node.step}")
        logs.append(format_state(node.state))

        if goal_test(node.state):
            logs.append("=> Tìm thấy trạng thái đích!")
            steps, states, costs = solution(node)
            return steps, states, costs, logs

        if depth(node) >= limit:
            logs.append("-> Cutoff vì đạt giới hạn độ sâu.")
            result = "cutoff"

        elif not is_cycle(node):
            for action in reversed(valid_actions(node.state)):
                child = child_node(node, action)

                new_zero = child.state.index(0)
                swapped_tile = node.state[new_zero]

                logs.append(f"\n  Thử move {action}:")
                logs.append(f"  Hoán đổi 0 với {swapped_tile}")
                logs.append(f"  Trạng thái tạo ra: {format_log_state(child.state)}")
                logs.append("  -> Thêm vào stack IDS.")

                frontier.append(child)

        else:
            logs.append("-> Bỏ qua vì bị lặp chu trình.")

    return result, logs


def iterative_deepening_search(initial_state, max_depth=50):
    all_logs = []

    for limit in range(max_depth + 1):
        result = depth_limited_search(initial_state, limit)

        if isinstance(result, tuple) and len(result) == 4:
            steps, states, costs, logs = result
            all_logs.extend(logs)
            return steps, states, costs, all_logs

        status, logs = result
        all_logs.extend(logs)

        if status != "cutoff":
            return "failure"

    return "failure"
# ===================== A* =====================
def astar(initial_state):
    logs = []

    g_start = 0
    h_start = misplaced_tiles(initial_state)
    f_start = g_start + h_start

    node = Node(
        state=initial_state,
        cost=g_start
    )

    frontier = []
    counter = 0

    heapq.heappush(frontier, (f_start, counter, node))

    frontier_g = {
        node.state: g_start
    }

    explored = {}

    logs.append("=== A* SEARCH LOG ===")
    logs.append(f"Initial State: {format_log_state(initial_state)}")
    logs.append(f"g(Start) = {g_start}")
    logs.append(f"h(Start) = {h_start}")
    logs.append(f"f(Start) = {f_start}")

    while frontier:
        current_f, _, node = heapq.heappop(frontier)

        g_current = inversion_count(node.state)
        h_current = misplaced_tiles(node.state)
        f_current = g_current + h_current

        logs.append("\n--------------------------------")
        logs.append(f"Đang xét node ở step = {node.step}")
        logs.append(format_state(node.state))
        logs.append(f"g(n) = {g_current}")
        logs.append(f"h(n) = {h_current}")
        logs.append(f"f(n) = {f_current}")

        if goal_test(node.state):
            logs.append("=> Tìm thấy trạng thái đích!")
            steps, states, costs = solution(node)
            return steps, states, costs, logs

        explored[node.state] = g_current

        for action in valid_actions(node.state):
            child = child_node(node, action)

            g_new = node.cost + inversion_count(child.state)
            h_new = misplaced_tiles(child.state)
            f_new = g_new + h_new

            new_zero = child.state.index(0)
            swapped_tile = node.state[new_zero]

            logs.append(f"\n  Thử move {action}:")
            logs.append(f"  Hoán đổi 0 với {swapped_tile}")
            logs.append(f"  Trạng thái tạo ra: {format_log_state(child.state)}")
            logs.append(f"  g(m) = số dãy ngược = {g_new}")
            logs.append(f"  h(m) = số ô sai = {h_new}")
            logs.append(f"  f(m) = g + h = {f_new}")

            if child.state in explored:
                if g_new >= explored[child.state]:
                    logs.append("  -> Bỏ qua: đã trong REACHED và g_new không tốt hơn.")
                    continue
                else:
                    logs.append("  -> Xóa khỏi REACHED vì g_new tốt hơn.")
                    del explored[child.state]

            if child.state in frontier_g:
                if g_new < frontier_g[child.state]:
                    logs.append("  -> Cập nhật node trong FRONTIER vì g_new tốt hơn.")
                    frontier_g[child.state] = g_new
                    counter += 1
                    heapq.heappush(frontier, (f_new, counter, child))
                else:
                    logs.append("  -> Bỏ qua: đã có trong FRONTIER và g_new không tốt hơn.")
            else:
                logs.append("  -> Thêm vào FRONTIER.")
                frontier_g[child.state] = g_new
                counter += 1
                heapq.heappush(frontier, (f_new, counter, child))

    return None


# ===================== IAS =====================

def ias_search(node, bound, path_states, logs):
    g_value = node.step
    h_value = misplaced_tiles(node.state)
    f_value = g_value + h_value

    logs.append("\n--------------------------------")
    logs.append(f"Đang xét node ở step = {node.step}")
    logs.append(format_state(node.state))
    logs.append(f"g(n) = số bước = {g_value}")
    logs.append(f"h(n) = số ô sai = {h_value}")
    logs.append(f"f(n) = g + h = {f_value}")
    logs.append(f"Giới hạn hiện tại = {bound}")

    if f_value > bound:
        logs.append("-> Cắt nhánh vì f(n) > giới hạn.")
        return f_value

    if goal_test(node.state):
        logs.append("=> Tìm thấy trạng thái đích!")
        return node

    min_next_bound = float("inf")

    for action in valid_actions(node.state):
        child = child_node(node, action)
        child.cost = child.step

        new_zero = child.state.index(0)
        swapped_tile = node.state[new_zero]
        child_g = child.step
        child_h = misplaced_tiles(child.state)
        child_f = child_g + child_h

        logs.append(f"\n  Thử move {action}:")
        logs.append(f"  Hoán đổi 0 với {swapped_tile}")
        logs.append(f"  Trạng thái tạo ra: {format_log_state(child.state)}")
        logs.append(f"  g(m) = số bước = {child_g}")
        logs.append(f"  h(m) = số ô sai = {child_h}")
        logs.append(f"  f(m) = g + h = {child_f}")

        if child.state in path_states:
            logs.append("  -> Bỏ qua: trạng thái bị lặp trong đường đi hiện tại.")
            continue

        path_states.add(child.state)
        result = ias_search(child, bound, path_states, logs)
        path_states.remove(child.state)

        if isinstance(result, Node):
            return result

        if result < min_next_bound:
            min_next_bound = result

    return min_next_bound


def ias(initial_state):
    logs = []
    node = Node(
        state=initial_state,
        cost=0
    )

    bound = misplaced_tiles(initial_state)

    logs.append("=== IAS SEARCH LOG ===")
    logs.append("IAS = Iterative A* Search")
    logs.append(f"Initial State: {format_log_state(initial_state)}")
    logs.append("g(Start) = số bước = 0")
    logs.append(f"h(Start) = số ô sai = {bound}")
    logs.append(f"f(Start) = g + h = {bound}")

    while True:
        logs.append("\n================================")
        logs.append(f"Lặp IAS với giới hạn f_limit = {bound}")

        path_states = {node.state}
        result = ias_search(node, bound, path_states, logs)

        if isinstance(result, Node):
            steps, states, costs = solution(result)
            return steps, states, costs, logs

        if result == float("inf"):
            logs.append("=> Không còn ngưỡng f mới để mở rộng. IAS thất bại.")
            return "failure"

        logs.append(f"=> Chưa tìm thấy goal trong giới hạn {bound}.")
        logs.append(f"=> Tăng giới hạn f_limit lên {result}.")
        bound = result


def IAS(Start):
    return ias(Start)


# ===================== SIMPLE HILL CLIMBING =====================

def simple_hill_climbing(initial_state):
    logs = []
    current = Node(
        state=initial_state,
        cost=misplaced_tiles(initial_state)
    )

    logs.append("=== SIMPLE HILL CLIMBING SEARCH LOG ===")
    logs.append(f"Initial State: {format_log_state(initial_state)}")
    logs.append(f"h(Start) = số ô sai = {misplaced_tiles(initial_state)}")

    while True:
        current_h = misplaced_tiles(current.state)

        logs.append("\n--------------------------------")
        logs.append(f"Trạng thái hiện tại ở step = {current.step}")
        logs.append(format_state(current.state))
        logs.append(f"h(Current) = số ô sai = {current_h}")

        if goal_test(current.state):
            logs.append("=> Tìm thấy trạng thái đích!")
            steps, states, costs = solution(current)
            return steps, states, costs, logs

        moved = False

        for action in valid_actions(current.state):
            next_state, _ = swap(current.state, action)
            next_node = Node(
                state=next_state,
                parent=current,
                action=action,
                step=current.step + 1,
                cost=misplaced_tiles(next_state)
            )

            next_h = misplaced_tiles(next_state)
            new_zero = next_state.index(0)
            swapped_tile = current.state[new_zero]

            logs.append(f"\n  Thử move {action}:")
            logs.append(f"  Hoán đổi 0 với {swapped_tile}")
            logs.append(f"  Trạng thái tạo ra: {format_log_state(next_state)}")
            logs.append(f"  h(Next) = số ô sai = {next_h}")

            if next_h < current_h:
                logs.append("  -> h(Next) nhỏ hơn h(Current), chọn trạng thái này và sang vòng lặp tiếp theo.")
                current = next_node
                moved = True
                break

            logs.append("  -> h(Next) không nhỏ hơn h(Current), thử lân cận tiếp theo.")

        if not moved:
            logs.append("\n=> Không có trạng thái lân cận nào tốt hơn.")
            logs.append("=> Dừng vì đạt cực đại cục bộ.")
            steps, states, costs = solution(current)
            return steps, states, costs, logs


def Simple_Hill_Climbing(Start):
    return simple_hill_climbing(Start)


# ===================== RANDOM RESTART HILL CLIMBING =====================

def random_restart_hill_climbing(initial_state, max_restart=30):
    logs = []

    logs.append("=== RANDOM RESTART HILL CLIMBING SEARCH LOG ===")
    logs.append(f"MAX_RESTART = {max_restart}")
    logs.append("h(n) = Manhattan distance")
    logs.append(f"Start ban đầu: {format_log_state(initial_state)}")

    for restart in range(1, max_restart + 1):
        current = Node(
            state=initial_state,
            cost=manhattan_distance(initial_state)
        )

        logs.append("\n================================")
        logs.append(f"Restart lần {restart}/{max_restart}")
        logs.append(f"Current_State = Start: {format_log_state(current.state)}")
        logs.append(f"h(Current) = Manhattan distance = {manhattan_distance(current.state)}")

        while True:
            current_h = manhattan_distance(current.state)

            logs.append("\n--------------------------------")
            logs.append(f"Trạng thái hiện tại ở step = {current.step}")
            logs.append(format_state(current.state))
            logs.append(f"h(Current) = Manhattan distance = {current_h}")

            if goal_test(current.state):
                logs.append("=> Tìm thấy trạng thái đích!")
                steps, states, costs = solution(current)
                return steps, states, costs, logs

            better_neighbors = []

            logs.append("\nSinh tất cả trạng thái lân cận:")

            for action in valid_actions(current.state):
                neighbor_state, _ = swap(current.state, action)
                neighbor_h = manhattan_distance(neighbor_state)
                new_zero = neighbor_state.index(0)
                swapped_tile = current.state[new_zero]

                logs.append(f"\n  Thử move {action}:")
                logs.append(f"  Hoán đổi 0 với {swapped_tile}")
                logs.append(f"  Neighbor: {format_log_state(neighbor_state)}")
                logs.append(f"  h(Neighbor) = Manhattan distance = {neighbor_h}")

                if neighbor_h < current_h:
                    neighbor_node = Node(
                        state=neighbor_state,
                        parent=current,
                        action=action,
                        step=current.step + 1,
                        cost=neighbor_h
                    )
                    better_neighbors.append(neighbor_node)
                    logs.append("  -> Tốt hơn Current, thêm vào Better_Neighbors.")
                else:
                    logs.append("  -> Không tốt hơn Current.")

            if not better_neighbors:
                logs.append("\nBetter_Neighbors rỗng.")
                logs.append("=> Lượt này bị kẹt ở cực tiểu cục bộ, chuyển sang restart tiếp theo.")
                break

            next_node = random.choice(better_neighbors)
            logs.append(f"\nChọn random từ Better_Neighbors: move {next_node.action}")
            logs.append(f"Current_State = {format_log_state(next_node.state)}")
            logs.append(f"h(Current) = Manhattan distance = {manhattan_distance(next_node.state)}")
            current = next_node

    logs.append("\n=> Chạy hết MAX_RESTART nhưng không chạm được Goal.")
    return "failure"


def Random_Restart_Hill_Climbing(Start):
    return random_restart_hill_climbing(Start)


# ===================== LOCAL BEAM SEARCH =====================

def random_node_from_start(initial_state, random_steps=10):
    current = Node(
        state=initial_state,
        cost=manhattan_distance(initial_state)
    )

    for _ in range(random_steps):
        action = random.choice(valid_actions(current.state))
        next_state, _ = swap(current.state, action)
        current = Node(
            state=next_state,
            parent=current,
            action=action,
            step=current.step + 1,
            cost=manhattan_distance(next_state)
        )

    return current


def local_beam_search(initial_state, k=2, random_steps=10):
    logs = []

    logs.append("=== LOCAL BEAM SEARCH LOG ===")
    logs.append(f"k = {k}")
    logs.append("h(n) = Manhattan distance")
    logs.append(f"Start: {format_log_state(initial_state)}")

    current_state_set = [
        random_node_from_start(initial_state, random_steps)
        for _ in range(k)
    ]

    logs.append("\nKhởi tạo Current_State_set:")
    for index, node in enumerate(current_state_set, start=1):
        logs.append(f"  Beam {index}: {format_log_state(node.state)}")
        logs.append(f"  h(Beam {index}) = Manhattan distance = {manhattan_distance(node.state)}")

        if goal_test(node.state):
            logs.append("=> Có trạng thái khởi tạo là Goal.")
            steps, states, costs = solution(node)
            return steps, states, costs, logs

    iteration = 1

    while True:
        logs.append("\n================================")
        logs.append(f"Vòng lặp Local Beam Search {iteration}")

        neighbor_states = []
        neighbor_seen = set()

        logs.append("\n2.1. Sinh trạng thái lân cận:")

        for beam_index, node in enumerate(current_state_set, start=1):
            current_h = manhattan_distance(node.state)

            logs.append(f"\nBeam {beam_index}:")
            logs.append(format_state(node.state))
            logs.append(f"h(State) = Manhattan distance = {current_h}")

            for action in valid_actions(node.state):
                neighbor_state, _ = swap(node.state, action)
                neighbor_h = manhattan_distance(neighbor_state)
                new_zero = neighbor_state.index(0)
                swapped_tile = node.state[new_zero]

                logs.append(f"\n  Thử move {action}:")
                logs.append(f"  Hoán đổi 0 với {swapped_tile}")
                logs.append(f"  Neighbor: {format_log_state(neighbor_state)}")
                logs.append(f"  h(Neighbor) = Manhattan distance = {neighbor_h}")

                if neighbor_h < current_h:
                    if neighbor_state in neighbor_seen:
                        logs.append("  -> Tốt hơn nhưng bị trùng, không thêm lại.")
                        continue

                    neighbor_node = Node(
                        state=neighbor_state,
                        parent=node,
                        action=action,
                        step=node.step + 1,
                        cost=neighbor_h
                    )
                    neighbor_states.append(neighbor_node)
                    neighbor_seen.add(neighbor_state)
                    logs.append("  -> Tốt hơn State hiện tại, thêm vào Neighbor_States.")
                else:
                    logs.append("  -> Không tốt hơn State hiện tại.")

        if not neighbor_states:
            logs.append("\nNeighbor_States rỗng.")
            logs.append("=> Không còn lân cận tốt hơn, Local Beam Search thất bại.")
            return "failure"

        logs.append("\n2.2. Kiểm tra đích:")
        for neighbor in neighbor_states:
            if goal_test(neighbor.state):
                logs.append(f"=> Tìm thấy Goal: {format_log_state(neighbor.state)}")
                steps, states, costs = solution(neighbor)
                return steps, states, costs, logs

        logs.append("=> Chưa có Neighbor nào là Goal.")

        logs.append("\n2.3. Sắp xếp Neighbor_States theo h(n) tăng dần:")
        neighbor_states.sort(key=lambda node: manhattan_distance(node.state))

        for index, node in enumerate(neighbor_states, start=1):
            logs.append(
                f"  {index}. h = {manhattan_distance(node.state)} | "
                f"{format_log_state(node.state)}"
            )

        current_state_set = neighbor_states[:k]

        logs.append(f"\nLấy {k} trạng thái tốt nhất làm Current_State_set mới:")
        for index, node in enumerate(current_state_set, start=1):
            logs.append(f"  Beam {index}: {format_log_state(node.state)}")
            logs.append(f"  h(Beam {index}) = Manhattan distance = {manhattan_distance(node.state)}")

        iteration += 1


def Local_Beam_Search(k, Start=None):
    if Start is None:
        Start = generate_random_state()
    return local_beam_search(Start, k)


# ===================== SIMULATED ANNEALING =====================

def manhattan_distance_to_goal(state, target_goal):
    distance = 0

    for i in range(9):
        value = state[i]

        if value != 0:
            current_row = i // 3
            current_col = i % 3

            goal_index = target_goal.index(value)
            goal_row = goal_index // 3
            goal_col = goal_index % 3

            distance += abs(current_row - goal_row) + abs(current_col - goal_col)

    return distance


def random_neighbor_node(node, target_goal):
    action = random.choice(valid_actions(node.state))
    next_state, _ = swap(node.state, action)

    return Node(
        state=next_state,
        parent=node,
        action=action,
        step=node.step + 1,
        cost=manhattan_distance_to_goal(next_state, target_goal)
    )


def simulated_annealing(start, target_goal=goal, t0=100.0, tmin=0.01, alpha=0.95):
    if not 0.95 <= alpha <= 0.99:
        raise ValueError("alpha phải nằm trong khoảng 0.95 <= alpha <= 0.99")

    logs = []
    current = Node(
        state=start,
        cost=manhattan_distance_to_goal(start, target_goal)
    )
    temperature = t0

    logs.append("=== SIMULATED ANNEALING SEARCH LOG ===")
    logs.append(f"Start: {format_log_state(start)}")
    logs.append(f"T0 = {t0}")
    logs.append(f"Tmin = {tmin}")
    logs.append(f"alpha = {alpha}")
    logs.append("h(n) = Manhattan distance")
    logs.append(f"h(Start) = {current.cost}")

    while temperature > tmin:
        current_h = manhattan_distance_to_goal(current.state, target_goal)

        logs.append("\n--------------------------------")
        logs.append(f"Step = {current.step}")
        logs.append(format_state(current.state))
        logs.append(f"T = {temperature:.6f}")
        logs.append(f"h(Current) = Manhattan distance = {current_h}")

        if current.state == target_goal:
            logs.append("=> Tìm thấy trạng thái đích!")
            steps, states, costs = solution(current)
            return steps, states, costs, logs

        next_node = random_neighbor_node(current, target_goal)
        next_h = manhattan_distance_to_goal(next_node.state, target_goal)
        delta = next_h - current_h
        new_zero = next_node.state.index(0)
        swapped_tile = current.state[new_zero]

        logs.append(f"\nRandomNeighbor: move {next_node.action}")
        logs.append(f"Hoán đổi 0 với {swapped_tile}")
        logs.append(f"Next_State: {format_log_state(next_node.state)}")
        logs.append(f"h(Next) = Manhattan distance = {next_h}")
        logs.append(f"Delta = h(Next) - h(Current) = {delta}")

        if delta < 0:
            logs.append("-> Delta < 0, nhận Next_State vì tốt hơn.")
            current = next_node
        else:
            probability = math.exp(-delta / temperature)
            random_value = random.random()

            logs.append(f"p = exp(-Delta / T) = {probability:.6f}")
            logs.append(f"Random(0, 1) = {random_value:.6f}")

            if random_value < probability:
                logs.append("-> Random < p, nhận Next_State dù không tốt hơn.")
                current = next_node
            else:
                logs.append("-> Random >= p, giữ Current_State.")

        temperature = alpha * temperature
        logs.append(f"Cập nhật T = alpha * T = {temperature:.6f}")

    logs.append("\n=> Dừng vì T <= Tmin.")
    logs.append("=> Trả về Current_State hiện tại.")
    steps, states, costs = solution(current)
    return steps, states, costs, logs


def SimulatedAnnealing(start, goal):
    return simulated_annealing(start, goal)


# ===================== GREEDY SEARCH =====================
def greedy_search(initial_state):
    logs = []

    node = Node(initial_state)

    frontier = []
    counter = 0

    h_start = manhattan_distance(initial_state)

    heapq.heappush(frontier, (h_start, counter, node))

    frontier_states = {node.state}
    reached = set()

    logs.append("=== GREEDY SEARCH LOG ===")
    logs.append(f"Initial State: {format_log_state(initial_state)}")
    logs.append(f"h(Start) = Manhattan distance = {h_start}")

    while frontier:
        h_current, _, node = heapq.heappop(frontier)

        if node.state in reached:
            continue

        frontier_states.discard(node.state)

        logs.append("\n--------------------------------")
        logs.append(f"Đang xét node ở step = {node.step}")
        logs.append(format_state(node.state))
        logs.append(f"h(n) = Manhattan distance = {manhattan_distance(node.state)}")

        if goal_test(node.state):
            logs.append("=> Tìm thấy trạng thái đích!")
            steps, states, costs = solution(node)
            return steps, states, costs, logs

        reached.add(node.state)

        for action in valid_actions(node.state):
            child = child_node(node, action)
            h_child = manhattan_distance(child.state)
 
            new_zero = child.state.index(0) 
            swapped_tile = node.state[new_zero]

            logs.append(f"\n  Thử move {action}:")
            logs.append(f"  Hoán đổi 0 với {swapped_tile}")
            logs.append(f"  Trạng thái tạo ra: {format_log_state(child.state)}")
            logs.append(f"  h(m) = Manhattan distance = {h_child}")

            if child.state in reached:
                logs.append("  -> Bỏ qua: đã có trong REACHED.")

            elif child.state in frontier_states:
                logs.append("  -> Bỏ qua: đã có trong FRONTIER.")

            else:
                counter += 1
                heapq.heappush(frontier, (h_child, counter, child))
                frontier_states.add(child.state)
                logs.append("  -> Thêm vào FRONTIER.")

    return None


# ===================== RANDOM STATE =====================

def generate_random_state():
    state = goal

    for _ in range(20):
        actions = valid_actions(state)
        action = random.choice(actions)
        state, _ = swap(state, action)

    return state


# ===================== GUI =====================

class EightPuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle Search Algorithms")

        self.current_state = generate_random_state()
        self.steps = []
        self.states = []
        self.costs = []
        self.index = 0
        self.algorithm_groups = {
            "Tìm kiếm không có thông tin": [
                "BFS",
                "DFS",
                "IDS",
                "UCS"
            ],
            "Tìm kiếm có thông tin": [
                "Greedy",
                "A*",
                "IAS"
            ],
            "Local Search": [
                "Simple Hill Climbing",
                "Random Restart HC",
                "Local Beam",
                "Simulated Annealing"
            ],
            "Constraint Satisfaction Problems": [
                "Backtracking",
                "Forward Checking",
                "AC-3",
                "Min-Conflicts"
            ]
        }

        title = tk.Label(
            root,
            text="8 Puzzle Solver: SEARCH - CSP - LOCAL SEARCH",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=10)

        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10)

        left_frame = tk.Frame(main_frame)
        left_frame.grid(row=0, column=0, padx=10, sticky="n")

        self.board_frame = tk.Frame(left_frame)
        self.board_frame.pack()

        self.tiles = []

        for i in range(9):
            tile = tk.Label(
                self.board_frame,
                text="",
                width=5,
                height=2,
                font=("Arial", 28, "bold"),
                borderwidth=2,
                relief="ridge",
                bg="white"
            )
            tile.grid(row=i // 3, column=i % 3, padx=5, pady=5)
            self.tiles.append(tile)

        control_frame = tk.Frame(left_frame)
        control_frame.pack(pady=10)

        tk.Label(
            control_frame,
            text="Loại:",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, padx=5)

        self.search_type_box = ttk.Combobox(
            control_frame,
            values=list(self.algorithm_groups.keys()),
            state="readonly",
            width=24,
            font=("Arial", 12)
        )
        self.search_type_box.current(0)
        self.search_type_box.grid(row=0, column=1, padx=5)
        self.search_type_box.bind("<<ComboboxSelected>>", self.on_search_type_selected)

        tk.Label(
            control_frame,
            text="Thuật toán:",
            font=("Arial", 12, "bold")
        ).grid(row=1, column=0, padx=5, pady=6)

        self.algorithm_box = ttk.Combobox(
            control_frame,
            values=self.algorithm_groups[self.search_type_box.get()],
            state="readonly",
            width=22,
            font=("Arial", 12)
        )
        self.algorithm_box.current(0)
        self.algorithm_box.grid(row=1, column=1, padx=5, pady=6)

        self.random_button = tk.Button(
            control_frame,
            text="Tạo random",
            width=16,
            font=("Arial", 11, "bold"),
            command=self.generate_random
        )
        self.random_button.grid(row=2, column=0, padx=5, pady=8)

        self.solve_button = tk.Button(
            control_frame,
            text="Giải",
            width=16,
            font=("Arial", 11, "bold"),
            command=self.auto_solve
        )
        self.solve_button.grid(row=2, column=1, padx=5, pady=8)

        self.info = tk.Label(
            left_frame,
            text="",
            font=("Arial", 12),
            fg="blue"
        )
        self.info.pack(pady=5)

        right_frame = tk.Frame(main_frame)
        right_frame.grid(row=0, column=1, padx=10, sticky="n")

        tk.Label(
            right_frame,
            text="Log xét trạng thái và hoán đổi",
            font=("Arial", 14, "bold")
        ).pack()

        self.log_text = tk.Text(
            right_frame,
            width=65,
            height=25,
            font=("Consolas", 9)
        )
        self.log_text.pack()

        result_frame = tk.Frame(root)
        result_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(
            result_frame,
            text="Kết quả từ trạng thái ban đầu đến đích",
            font=("Arial", 14, "bold")
        ).pack(anchor="w")

        self.result_text = tk.Text(
            result_frame,
            width=120,
            height=12,
            font=("Consolas", 10)
        )
        self.result_text.pack(fill="x")

        self.draw_board(self.current_state)
        self.info.config(text="Chọn thuật toán rồi bấm Auto Solve.")

    def draw_board(self, state):
        for i, value in enumerate(state):
            if value is None or value == 0:
                self.tiles[i].config(text="", bg="lightgray")
            else:
                self.tiles[i].config(text=str(value), bg="white")

    def on_search_type_selected(self, event=None):
        search_type = self.search_type_box.get()
        algorithms = self.algorithm_groups.get(search_type, [])

        self.algorithm_box.config(values=algorithms)

        if algorithms:
            self.algorithm_box.current(0)

    def generate_random(self):
        self.current_state = generate_random_state()

        self.steps = []
        self.states = []
        self.costs = []
        self.index = 0

        self.draw_board(self.current_state)

        self.log_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)

        self.info.config(text="Đã tạo trạng thái ngẫu nhiên.")

    def auto_solve(self):
        algorithm = self.algorithm_box.get()

        self.log_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)

        if algorithm == "BFS":
            result = bfs(self.current_state)
        elif algorithm == "DFS":
            result = dfs(self.current_state)
        elif algorithm == "IDS":
            result = iterative_deepening_search(self.current_state)
        elif algorithm == "UCS":
            result = ucs(self.current_state)
        elif algorithm == "A*":
            result = astar(self.current_state)
        elif algorithm == "IAS":
            result = ias(self.current_state)
        elif algorithm == "Greedy":
            result = greedy_search(self.current_state)
        elif algorithm == "Simple Hill Climbing":
            result = simple_hill_climbing(self.current_state)
        elif algorithm == "Random Restart HC":
            result = random_restart_hill_climbing(self.current_state)
        elif algorithm == "Local Beam":
            result = local_beam_search(self.current_state, k=2)
        elif algorithm == "Simulated Annealing":
            result = simulated_annealing(self.current_state, goal)
        elif algorithm == "Min-Conflicts":
            result = min_conflicts_8puzzle(self.current_state, max_steps=1000)
            if isinstance(result, tuple) and result[0] == "failure":
                _, _, _, logs_fail = result
                self.log_text.insert(tk.END, "\n".join(logs_fail))
                self.info.config(text="Min-Conflicts: Không tìm được lời giải.")
                return
        elif algorithm == "Backtracking":
            result = backtracking_8puzzle(self.current_state)
            if isinstance(result, tuple) and result[0] == "failure":
                _, _, _, logs_fail = result
                self.log_text.insert(tk.END, "\n".join(logs_fail))
                self.info.config(text="Backtracking: Không tìm được lời giải.")
                return
        elif algorithm == "Forward Checking":
            result = forward_checking_8puzzle(self.current_state)
            if isinstance(result, tuple) and result[0] == "failure":
                _, _, _, logs_fail = result
                self.log_text.insert(tk.END, "\n".join(logs_fail))
                self.info.config(text="Forward Checking: Không tìm được lời giải.")
                return
        elif algorithm == "AC-3":
            result = ac3_8puzzle(self.current_state)
            if isinstance(result, tuple) and result[0] == "failure":
                _, _, _, logs_fail = result
                self.log_text.insert(tk.END, "\n".join(logs_fail))
                self.info.config(text="AC-3: Không tìm được lời giải.")
                return
        else:
            self.info.config(text="Chưa chọn thuật toán.")
            return

        if result is None or result == "failure":
            self.info.config(text="Không tìm thấy lời giải.")
            return

        self.steps, self.states, self.costs, search_logs = result
        self.index = 0

        self.log_text.insert(tk.END, "\n".join(search_logs))
        self.log_text.insert(tk.END, "\n\n=== SOLUTION PATH ANIMATION ===\n\n")
        self.log_text.see(tk.END)

        self.random_button.config(state="disabled")
        self.solve_button.config(state="disabled")
        self.search_type_box.config(state="disabled")
        self.algorithm_box.config(state="disabled")

        self.show_result_path()
        self.show_step()

    def show_result_path(self):
        algorithm = self.algorithm_box.get()

        self.result_text.insert(tk.END, f"Thuật toán: {algorithm}\n")
        self.result_text.insert(tk.END, f"Tổng số bước đi: {len(self.steps)}\n")

        if algorithm == "UCS":
            self.result_text.insert(
                tk.END,
                f"Tổng chi phí UCS: {self.costs[-1]}\n"
            )

        self.result_text.insert(tk.END, "\nTrạng thái ban đầu:\n")
        self.result_text.insert(tk.END, format_state(self.states[0]))

        if algorithm == "UCS":
            self.result_text.insert(
                tk.END,
                f"\nCost ban đầu = {self.costs[0]}"
            )
        elif algorithm == "Simple Hill Climbing":
            h_value = misplaced_tiles(self.states[0])
            self.result_text.insert(
                tk.END,
                f"\nh(n) = số ô sai = {h_value}"
            )
        elif algorithm == "Random Restart HC":
            h_value = manhattan_distance(self.states[0])
            self.result_text.insert(
                tk.END,
                f"\nh(n) = Manhattan distance = {h_value}"
            )
        elif algorithm == "Local Beam":
            h_value = manhattan_distance(self.states[0])
            self.result_text.insert(
                tk.END,
                f"\nh(n) = Manhattan distance = {h_value}"
            )
        elif algorithm == "Simulated Annealing":
            h_value = manhattan_distance(self.states[0])
            self.result_text.insert(
                tk.END,
                f"\nh(n) = Manhattan distance = {h_value}"
            )
        elif algorithm == "IAS":
            g_value = 0
            h_value = misplaced_tiles(self.states[0])
            f_value = g_value + h_value
            self.result_text.insert(
                tk.END,
                f"\ng(n) = số bước = {g_value}"
                f"\nh(n) = số ô sai = {h_value}"
                f"\nf(n) = g + h = {f_value}"
            )
        elif algorithm in ["Backtracking", "Forward Checking", "AC-3", "Min-Conflicts"]:
            conflicts = _count_conflicts_mc(self.states[0])
            self.result_text.insert(
                tk.END,
                f"\nSố ô xung đột = {conflicts}"
            )
        self.result_text.insert(tk.END, "\n\n")

        for i in range(1, len(self.states)):
            self.result_text.insert(
                tk.END,
                f"Step {i}: {self.steps[i - 1]}\n"
            )

            self.result_text.insert(tk.END, format_state(self.states[i]))
            if algorithm == "A*":
                g_value = inversion_count(self.states[i])
                h_value = misplaced_tiles(self.states[i])
                f_value = g_value + h_value

                self.result_text.insert(
                    tk.END,
                    f"\ng(n) = {g_value}"
                    f"\nh(n) = {h_value}"
                    f"\nf(n) = {f_value}"
                )

            if algorithm == "IAS":
                g_value = i
                h_value = misplaced_tiles(self.states[i])
                f_value = g_value + h_value

                self.result_text.insert(
                    tk.END,
                    f"\ng(n) = số bước = {g_value}"
                    f"\nh(n) = số ô sai = {h_value}"
                    f"\nf(n) = g + h = {f_value}"
                )
            
            if algorithm == "Greedy":
                h_value = manhattan_distance(self.states[i])

                self.result_text.insert(
                    tk.END,
                    f"\nh(n) = Manhattan distance = {h_value}"
                )
            if algorithm == "Random Restart HC":
                h_value = manhattan_distance(self.states[i])

                self.result_text.insert(
                    tk.END,
                    f"\nh(n) = Manhattan distance = {h_value}"
                )
            if algorithm == "Local Beam":
                h_value = manhattan_distance(self.states[i])

                self.result_text.insert(
                    tk.END,
                    f"\nh(n) = Manhattan distance = {h_value}"
                )
            if algorithm == "Simulated Annealing":
                h_value = manhattan_distance(self.states[i])

                self.result_text.insert(
                    tk.END,
                    f"\nh(n) = Manhattan distance = {h_value}"
                )
            if algorithm == "Simple Hill Climbing":
                h_value = misplaced_tiles(self.states[i])

                self.result_text.insert(
                    tk.END,
                    f"\nh(n) = số ô sai = {h_value}"
                )
            if algorithm == "UCS":
                current_state_cost = misplaced_tiles(self.states[i])
                self.result_text.insert(
                    tk.END,
                    f"\nCost trạng thái = {current_state_cost}"
                    f"\nTổng cost = {self.costs[i]}"
                )
            if algorithm in ["Backtracking", "Forward Checking", "AC-3", "Min-Conflicts"]:
                conflicts = _count_conflicts_mc(self.states[i])
                self.result_text.insert(
                    tk.END,
                    f"\nSố ô xung đột = {conflicts}"
                )

            self.result_text.insert(tk.END, "\n\n")

        if goal_test(self.states[-1]):
            self.result_text.insert(tk.END, "Đã tới trạng thái đích.\n")
        elif algorithm == "Simple Hill Climbing":
            self.result_text.insert(tk.END, "Dừng ở cực đại cục bộ, chưa tới trạng thái đích.\n")
        elif algorithm == "Simulated Annealing":
            self.result_text.insert(tk.END, "Dừng vì T <= Tmin, chưa tới trạng thái đích.\n")
        else:
            self.result_text.insert(tk.END, "Chưa tới trạng thái đích.\n")

    def show_step(self):
        if self.index < len(self.states):
            state = self.states[self.index]
            self.draw_board(state)

            algorithm = self.algorithm_box.get()

            if self.index == 0:
                self.info.config(
                    text=f"Initial State | Total moves: {len(self.steps)}"
                )

                self.log_text.insert(
                    tk.END,
                    f"Step 0 Solution: Initial State\n"
                    f"{format_state(state)}\n\n"
                )

            else:
                move = self.steps[self.index - 1]

                previous_state = self.states[self.index - 1]
                current_state = self.states[self.index]

                # CSP algorithms: trạng thái chuyển không phải hoán đổi ô trống
                if algorithm in ["Backtracking", "Forward Checking", "AC-3", "Min-Conflicts"]:
                    conflicts = _count_conflicts_mc(current_state)

                    self.info.config(
                        text=f"Step {self.index}/{len(self.steps)} | {move} | Xung đột: {conflicts}"
                    )

                    self.log_text.insert(
                        tk.END,
                        f"Step {self.index} Solution: {move}\n"
                        f"Số ô xung đột = {conflicts}\n"
                        f"{format_state(current_state)}\n\n"
                    )

                else:
                    new_zero = current_state.index(0)
                    swapped_tile = previous_state[new_zero]

                    if algorithm == "UCS":
                        current_state_cost = misplaced_tiles(current_state)

                        self.info.config(
                            text=f"Step {self.index}/{len(self.steps)} | Move: {move} | Cost: {self.costs[self.index]}"
                        )

                        self.log_text.insert(
                            tk.END,
                            f"Step {self.index} Solution: Move {move}\n"
                            f"Hoán đổi 0 với {swapped_tile}\n"
                            f"Số ô khác goal = {current_state_cost}\n"
                            f"Tổng cost = {self.costs[self.index]}\n"
                            f"{format_state(current_state)}\n\n"
                        )

                    elif algorithm == "Simple Hill Climbing":
                        h_value = misplaced_tiles(current_state)

                        self.info.config(
                            text=f"Step {self.index}/{len(self.steps)} | Move: {move} | h(n): {h_value}"
                        )

                        self.log_text.insert(
                            tk.END,
                            f"Step {self.index} Solution: Move {move}\n"
                            f"Hoán đổi 0 với {swapped_tile}\n"
                            f"h(n) = số ô sai = {h_value}\n"
                            f"{format_state(current_state)}\n\n"
                        )

                    elif algorithm == "IAS":
                        g_value = self.index
                        h_value = misplaced_tiles(current_state)
                        f_value = g_value + h_value

                        self.info.config(
                            text=f"Step {self.index}/{len(self.steps)} | Move: {move} | f(n): {f_value}"
                        )

                        self.log_text.insert(
                            tk.END,
                            f"Step {self.index} Solution: Move {move}\n"
                            f"Hoán đổi 0 với {swapped_tile}\n"
                            f"g(n) = số bước = {g_value}\n"
                            f"h(n) = số ô sai = {h_value}\n"
                            f"f(n) = g + h = {f_value}\n"
                            f"{format_state(current_state)}\n\n"
                        )

                    elif algorithm == "Random Restart HC":
                        h_value = manhattan_distance(current_state)

                        self.info.config(
                            text=f"Step {self.index}/{len(self.steps)} | Move: {move} | h(n): {h_value}"
                        )

                        self.log_text.insert(
                            tk.END,
                            f"Step {self.index} Solution: Move {move}\n"
                            f"Hoán đổi 0 với {swapped_tile}\n"
                            f"h(n) = Manhattan distance = {h_value}\n"
                            f"{format_state(current_state)}\n\n"
                        )

                    elif algorithm == "Local Beam":
                        h_value = manhattan_distance(current_state)

                        self.info.config(
                            text=f"Step {self.index}/{len(self.steps)} | Move: {move} | h(n): {h_value}"
                        )

                        self.log_text.insert(
                            tk.END,
                            f"Step {self.index} Solution: Move {move}\n"
                            f"Hoán đổi 0 với {swapped_tile}\n"
                            f"h(n) = Manhattan distance = {h_value}\n"
                            f"{format_state(current_state)}\n\n"
                        )

                    elif algorithm == "Simulated Annealing":
                        h_value = manhattan_distance(current_state)

                        self.info.config(
                            text=f"Step {self.index}/{len(self.steps)} | Move: {move} | h(n): {h_value}"
                        )

                        self.log_text.insert(
                            tk.END,
                            f"Step {self.index} Solution: Move {move}\n"
                            f"Hoán đổi 0 với {swapped_tile}\n"
                            f"h(n) = Manhattan distance = {h_value}\n"
                            f"{format_state(current_state)}\n\n"
                        )

                    else:
                        self.info.config(
                            text=f"Step {self.index}/{len(self.steps)} | Move: {move}"
                        )

                        self.log_text.insert(
                            tk.END,
                            f"Step {self.index} Solution: Move {move}\n"
                            f"Hoán đổi 0 với {swapped_tile}\n"
                            f"{format_state(current_state)}\n\n"
                        )

            self.log_text.see(tk.END)

            self.index += 1
            self.root.after(700, self.show_step)

        else:
            self.current_state = self.states[-1]

            self.random_button.config(state="normal")
            self.solve_button.config(state="normal")
            self.search_type_box.config(state="readonly")
            self.algorithm_box.config(state="readonly")

            if goal_test(self.current_state):
                self.info.config(text="Đã giải xong!")
            elif algorithm == "Simulated Annealing":
                self.info.config(text="Dừng vì T <= Tmin.")
            else:
                self.info.config(text="Dừng ở cực đại cục bộ.")


if __name__ == "__main__":
    root = tk.Tk()
    app = EightPuzzleApp(root)
    root.mainloop()
