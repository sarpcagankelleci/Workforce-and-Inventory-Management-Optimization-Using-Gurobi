#!/usr/bin/env python
# coding: utf-8

# INDR 372 HW3 Sarp Çağan Kelleci, Tan Karahasanoğlu

# #Question 1

# #Part A

# In[1]:


import gurobipy as gp
from gurobipy import GRB


# In[3]:


# Parameters
monthly_demand = [0, 2500, 2600, 4200, 3400, 2500, 4500, 1500, 1800, 1900, 2600, 3100, 3600]
workdays_per_month = [0, 21, 14, 20, 23, 18, 15, 20, 14, 20, 22, 20, 21]
manufacturing_cost_per_case = 120
selling_price_per_case = 220
firing_cost_per_worker = 10000
hiring_cost_per_worker = 4000
holding_cost_per_case_per_month = 4.4
initial_workers = 21
initial_inventory = 600
final_inventory_target = 2300
hours_per_case = 0.2
hours_per_workday = 8

# Initialize model
model = gp.Model("TomKon Workforce and Inventory Management")

# Number of months including initial and final points
num_months = 13

# Decision Variables
num_workers = model.addVar(name="num_workers", vtype=GRB.INTEGER, lb=0)
hiring = model.addVar(name="hiring", vtype=GRB.INTEGER, lb=0)
firing = model.addVar(name="firing", vtype=GRB.INTEGER, lb=0)
inventory = model.addVars(num_months, name="inventory", vtype=GRB.CONTINUOUS, lb=0)
production = model.addVars(num_months, name="production", vtype=GRB.CONTINUOUS, lb=0)

# Objective Function: Minimize the number of workers
model.setObjective(num_workers, GRB.MINIMIZE)

# Constraints
# Workforce balance
model.addConstr(num_workers == initial_workers + hiring - firing, "workforce_balance")

# Initial inventory
model.addConstr(inventory[0] == initial_inventory, "initial_inventory")

# Inventory balance constraints
for t in range(1, num_months):
    model.addConstr(inventory[t] == inventory[t - 1] + production[t] - monthly_demand[t], f"inventory_balance_{t}")

# Production capacity constraints
for t in range(1, num_months):
    model.addConstr(hours_per_case * production[t] <= workdays_per_month[t] * num_workers, f"production_capacity_{t}")

# End-of-year inventory target
model.addConstr(inventory[num_months - 1] == final_inventory_target, "end_of_year_inventory")

# Solve model
model.optimize()

# Output results
if model.status == GRB.OPTIMAL:
    print(f"Optimal number of workers: {round(num_workers.X)}")
    for t in range(0, num_months):
        print(f"Month {t}: Production = {round(production[t].X)}, Inventory = {round(inventory[t].X)}")
    total_manufacturing_cost = manufacturing_cost_per_case * sum(round(production[t].X) for t in range(1, num_months))
    total_holding_cost = holding_cost_per_case_per_month * sum(round(inventory[t].X) for t in range(1, num_months))
    total_cost = total_manufacturing_cost + total_holding_cost
    print(f"Total cost: {round(total_cost)}")
else:
    print("No optimal solution found.")


# #Part B

# In[4]:


import gurobipy as gp
from gurobipy import GRB

# Parameters
monthly_demand = [0, 2500, 2600, 4200, 3400, 2500, 4500, 1500, 1800, 1900, 2600, 3100, 3600]
workdays_per_month = [0, 21, 14, 20, 23, 18, 15, 20, 14, 20, 22, 20, 21]
manufacturing_cost_per_case = 120
holding_cost_per_case_per_month = 4.4
initial_workers = 21
initial_inventory = 600
final_inventory_target = 2300
hours_per_case = 0.2
hours_per_workday = 8
hiring_cost_per_worker = 4000
firing_cost_per_worker = 10000

# Initialize model
model = gp.Model("TomKon Workforce and Inventory Management")

# Number of months including initial and final points
num_months = 13

# Decision Variables
workers = model.addVars(num_months, name="workers", vtype=GRB.INTEGER, lb=0)
hiring = model.addVars(num_months, name="hiring", vtype=GRB.INTEGER, lb=0)
firing = model.addVars(num_months, name="firing", vtype=GRB.INTEGER, lb=0)
inventory = model.addVars(num_months, name="inventory", vtype=GRB.CONTINUOUS, lb=0)
production = model.addVars(num_months, name="production", vtype=GRB.CONTINUOUS, lb=0)

# Objective Function: Minimize total cost
total_manufacturing_cost = gp.quicksum(manufacturing_cost_per_case * production[t] for t in range(1, num_months))
total_holding_cost = gp.quicksum(holding_cost_per_case_per_month * inventory[t] for t in range(1, num_months))
total_hiring_cost = gp.quicksum(hiring_cost_per_worker * hiring[t] for t in range(1, num_months))
total_firing_cost = gp.quicksum(firing_cost_per_worker * firing[t] for t in range(1, num_months))
total_cost = total_manufacturing_cost + total_holding_cost + total_hiring_cost + total_firing_cost
model.setObjective(total_cost, GRB.MINIMIZE)

# Constraints
# Initial inventory
model.addConstr(inventory[0] == initial_inventory, "initial_inventory")

# Inventory balance constraints
for t in range(1, num_months):
    model.addConstr(inventory[t] == inventory[t - 1] + production[t] - monthly_demand[t], f"inventory_balance_{t}")

# Production capacity constraints
for t in range(1, num_months):
    model.addConstr(hours_per_case * production[t] <= workdays_per_month[t] * workers[t], f"production_capacity_{t}")

# Workforce balance constraints
model.addConstr(workers[0] == initial_workers, "initial_workforce_balance")
for t in range(1, num_months):
    model.addConstr(workers[t] == workers[t - 1] + hiring[t] - firing[t], f"workforce_balance_{t}")

# End-of-year inventory target
model.addConstr(inventory[num_months - 1] == final_inventory_target, "end_of_year_inventory")

# Solve model
model.optimize()

# Output results
if model.status == GRB.OPTIMAL:
    for t in range(num_months):
        print(f"Month {t}: Workers = {round(workers[t].X)}, Hiring = {round(hiring[t].X)}, Firing = {round(firing[t].X)}, Production = {round(production[t].X)}, Inventory = {round(inventory[t].X)}")
    total_manufacturing_cost = manufacturing_cost_per_case * sum(round(production[t].X) for t in range(1, num_months))
    total_holding_cost = holding_cost_per_case_per_month * sum(round(inventory[t].X) for t in range(1, num_months))
    total_hiring_cost = hiring_cost_per_worker * sum(round(hiring[t].X) for t in range(1, num_months))
    total_firing_cost = firing_cost_per_worker * sum(round(firing[t].X) for t in range(1, num_months))
    total_cost = total_manufacturing_cost + total_holding_cost + total_hiring_cost + total_firing_cost
    print(f"Total cost: {round(total_cost)}")
else:
    print("No optimal solution found.")


# Explanation:
# 
# Decision Variables:
# production[m]: Number of cases produced in month 𝑚
# inventory[m]: Inventory level at the end of month 𝑚
# workers[m]: Number of workers in month 𝑚
# hiring[m]: Number of workers hired in month 𝑚
# layoff[m]: Number of workers laid off in month 𝑚
# 
# Constraints:
# Initial inventory and inventory balance constraints.
# Production capacity constraint based on the number of workers.
# Workforce adjustment constraints to account for hiring and layoff.
# End-of-year inventory target constraint.
# 
# Objective Function:
# The total cost to be minimized includes manufacturing costs, storage costs, hiring costs, and layoff costs.
# 
# This code solves the linear program to find the optimal plan for hiring and firing workers each month to minimize the total costs while meeting the production and inventory requirements. 

# #Part C

# In[5]:


import gurobipy as gp
from gurobipy import GRB

# Parameters
monthly_demand = [0, 2500, 2600, 4200, 3400, 2500, 4500, 1500, 1800, 1900, 2600, 3100, 3600]
workdays_per_month = [0, 21, 14, 20, 23, 18, 15, 20, 14, 20, 22, 20, 21]
manufacturing_cost_per_case = 120
holding_cost_per_case_per_month = 4.4
initial_workers = 21
initial_inventory = 600
final_inventory_target = 2300
hours_per_case = 0.2
hours_per_workday = 8
hiring_cost_per_worker = 4000
firing_cost_per_worker = 10000

# Initialize model
model = gp.Model("TomKon Workforce and Inventory Management")

# Number of months including initial and final points
num_months = 13

# Decision Variables
workers = model.addVars(num_months, name="workers", vtype=GRB.INTEGER, lb=0)
hiring = model.addVars(num_months, name="hiring", vtype=GRB.INTEGER, lb=0)
firing = model.addVars(num_months, name="firing", vtype=GRB.INTEGER, lb=0)
inventory = model.addVars(num_months, name="inventory", vtype=GRB.CONTINUOUS, lb=0)
production = model.addVars(num_months, name="production", vtype=GRB.CONTINUOUS, lb=0)

# Objective Function: Minimize total cost
total_manufacturing_cost = gp.quicksum(manufacturing_cost_per_case * production[t] for t in range(1, num_months))
total_holding_cost = gp.quicksum(holding_cost_per_case_per_month * inventory[t] for t in range(1, num_months))
total_hiring_cost = gp.quicksum(hiring_cost_per_worker * hiring[t] for t in range(1, num_months))
total_firing_cost = gp.quicksum(firing_cost_per_worker * firing[t] for t in range(1, num_months))
total_cost = total_manufacturing_cost + total_holding_cost + total_hiring_cost + total_firing_cost
model.setObjective(total_cost, GRB.MINIMIZE)

# Constraints
# Initial inventory
model.addConstr(inventory[0] == initial_inventory, "initial_inventory")

# Inventory balance constraints
for t in range(1, num_months):
    model.addConstr(inventory[t] == inventory[t - 1] + production[t] - monthly_demand[t], f"inventory_balance_{t}")

# Production capacity constraints
for t in range(1, num_months):
    model.addConstr(hours_per_case * production[t] <= workdays_per_month[t] * workers[t], f"production_capacity_{t}")

# Workforce balance constraints
model.addConstr(workers[0] == initial_workers, "initial_workforce_balance")
for t in range(1, num_months):
    model.addConstr(workers[t] == workers[t - 1] + hiring[t] - firing[t], f"workforce_balance_{t}")

# Workforce change constraint (30%)
for t in range(1, num_months):
    model.addConstr(workers[t] <= 1.3 * workers[t - 1], f"workforce_increase_limit_{t}")
    model.addConstr(workers[t] >= 0.7 * workers[t - 1], f"workforce_decrease_limit_{t}")

# End-of-year inventory target
model.addConstr(inventory[num_months - 1] == final_inventory_target, "end_of_year_inventory")

# Solve model
model.optimize()

# Output results
if model.status == GRB.OPTIMAL:
    for t in range(num_months):
        print(f"Month {t}: Workers = {round(workers[t].X)}, Hiring = {round(hiring[t].X)}, Firing = {round(firing[t].X)}, Production = {round(production[t].X)}, Inventory = {round(inventory[t].X)}")
    total_manufacturing_cost = manufacturing_cost_per_case * sum(round(production[t].X) for t in range(1, num_months))
    total_holding_cost = holding_cost_per_case_per_month * sum(round(inventory[t].X) for t in range(1, num_months))
    total_hiring_cost = hiring_cost_per_worker * sum(round(hiring[t].X) for t in range(1, num_months))
    total_firing_cost = firing_cost_per_worker * sum(round(firing[t].X) for t in range(1, num_months))
    total_cost = total_manufacturing_cost + total_holding_cost + total_hiring_cost + total_firing_cost
    print(f"Total cost: {round(total_cost)}")
else:
    print("No optimal solution found.")


# Explanation:
# 
# 30% Workforce Change Constraint:
# 
# model.addConstr(workers[m] <= 1.3 * workers[m-1], f"Workforce_Change_Upper_{m}"): Ensures the workforce in month m does not exceed 130% of the workforce in month 𝑚 − 1
# 
# model.addConstr(workers[m] >= 0.7 * workers[m-1], f"Workforce_Change_Lower_{m}"): Ensures the workforce in month 𝑚 is at least 70% of the workforce in month 𝑚 − 1
# 
# This code ensures that the workforce changes are limited to within 30% from month to month while minimizing the total costs.

# #Part D

# In[53]:


import gurobipy as gp
from gurobipy import GRB

# Parameters
monthly_demand = [0, 2500, 2600, 4200, 3400, 2500, 4500, 1500, 1800, 1900, 2600, 3100, 3600]
workdays_per_month = [0, 21, 14, 20, 23, 18, 15, 20, 14, 20, 22, 20, 21]
manufacturing_cost_per_case = 120
holding_cost_per_case_per_month = 4.4
initial_workers = 21
initial_inventory = 600
final_inventory_target = 2300
hours_per_case = 0.2
hours_per_workday = 8
hiring_cost_per_worker = 4000
firing_cost_per_worker = 10000
extra_manufacturing_cost_per_case = 150
production_threshold = 3250

# Initialize model
model = gp.Model("TomKon Workforce and Inventory Management")

# Number of months including initial and final points
num_months = 13

# Decision Variables
workers = model.addVars(num_months, name="workers", vtype=GRB.INTEGER, lb=0)
hiring = model.addVars(num_months, name="hiring", vtype=GRB.INTEGER, lb=0)
firing = model.addVars(num_months, name="firing", vtype=GRB.INTEGER, lb=0)
inventory = model.addVars(num_months, name="inventory", vtype=GRB.CONTINUOUS, lb=0)
production = model.addVars(num_months, name="production", vtype=GRB.CONTINUOUS, lb=0)
excess_production = model.addVars(num_months, name="excess_production", vtype=GRB.CONTINUOUS, lb=0)

# Objective Function: Minimize total cost
total_manufacturing_cost = gp.quicksum(manufacturing_cost_per_case * production[t] + extra_manufacturing_cost_per_case * excess_production[t] for t in range(1, num_months))
total_holding_cost = gp.quicksum(holding_cost_per_case_per_month * inventory[t] for t in range(1, num_months))
total_hiring_cost = gp.quicksum(hiring_cost_per_worker * hiring[t] for t in range(1, num_months))
total_firing_cost = gp.quicksum(firing_cost_per_worker * firing[t] for t in range(1, num_months))
total_cost = total_manufacturing_cost + total_holding_cost + total_hiring_cost + total_firing_cost
model.setObjective(total_cost, GRB.MINIMIZE)

# Constraints
# Initial inventory
model.addConstr(inventory[0] == initial_inventory, "initial_inventory")

# Inventory balance constraints
for t in range(1, num_months):
    model.addConstr(inventory[t] == inventory[t - 1] + production[t] + excess_production[t] - monthly_demand[t], f"inventory_balance_{t}")

# Production capacity constraints
for t in range(1, num_months):
    model.addConstr(hours_per_case * (production[t] + excess_production[t]) <= workdays_per_month[t] * workers[t], f"production_capacity_{t}")
    model.addConstr(production[t] <= production_threshold, f"production_threshold_{t}")
    
# Workforce balance constraints
model.addConstr(workers[0] == initial_workers, "initial_workforce_balance")
for t in range(1, num_months):
    model.addConstr(workers[t] == workers[t - 1] + hiring[t] - firing[t], f"workforce_balance_{t}")

# Workforce change constraint (30%)
for t in range(1, num_months):
    model.addConstr(workers[t] <= 1.3 * workers[t - 1], f"workforce_increase_limit_{t}")
    model.addConstr(workers[t] >= 0.7 * workers[t - 1], f"workforce_decrease_limit_{t}")

# Excess production constraint
for t in range(1, num_months):
    model.addConstr(excess_production[t] >= production[t] - production_threshold, f"excess_production_{t}")
    model.addConstr(excess_production[t] >= 0, f"non_negative_excess_production_{t}")

# End-of-year inventory target
model.addConstr(inventory[num_months - 1] == final_inventory_target, "end_of_year_inventory")

# Solve model
model.optimize()

# Output results
if model.status == GRB.OPTIMAL:
    for t in range(num_months):
        print(f"Month {t}: Workers = {round(workers[t].X)}, Hiring = {round(hiring[t].X)}, Firing = {round(firing[t].X)}, Production = {round(production[t].X)}, Excess Production = {round(excess_production[t].X)}, Inventory = {round(inventory[t].X)}")
    total_manufacturing_cost = manufacturing_cost_per_case * sum(round(production[t].X) for t in range(1, num_months))
    total_extra_manufacturing_cost = extra_manufacturing_cost_per_case * sum(round(excess_production[t].X) for t in range(1, num_months))
    total_holding_cost = holding_cost_per_case_per_month * sum(round(inventory[t].X) for t in range(1, num_months))
    total_hiring_cost = hiring_cost_per_worker * sum(round(hiring[t].X) for t in range(1, num_months))
    total_firing_cost = firing_cost_per_worker * sum(round(firing[t].X) for t in range(1, num_months))
    total_cost = total_manufacturing_cost + total_extra_manufacturing_cost + total_holding_cost + total_hiring_cost + total_firing_cost
    print(f"Total manufacturing cost: {total_manufacturing_cost + total_extra_manufacturing_cost:.2f} TL")
    print(f"Total holding cost: {total_holding_cost:.2f} TL")
    print(f"Total hiring cost: {total_hiring_cost:.2f} TL")
    print(f"Total firing cost: {total_firing_cost:.2f} TL")
    print(f"Total cost: {round(total_cost)} TL")
else:
    print("No optimal solution found.")


# Explanation:
# New Decision Variables:
# 
# regular_production[m]: Number of units produced up to the threshold (3250 cases) in month 𝑚
# excess_production[m]: Number of units produced above the threshold in month 𝑚
# Constraints for Production:
# 
# model.addConstr(regular_production[m] <= production_threshold, f"Regular_Production_Limit_{m}"): Ensures that regular production does not exceed 3250 cases.
# model.addConstr(production[m] == regular_production[m] + excess_production[m], f"Total_Production_{m}"): Ensures total production is the sum of regular and excess production.
# Objective Function:
# 
# Adjusted to account for different manufacturing costs for regular and excess production:
# manufacture_cost_per_case * regular_production[m]: Standard manufacturing cost for regular production.
# increased_manufacture_cost_per_case * excess_production[m]: Increased manufacturing cost for excess production.
# This modified implementation accounts for the increased manufacturing cost when production exceeds 3250 units. 

# #Part E

# In[54]:


import gurobipy as gp
from gurobipy import GRB

# Parameters
monthly_demand = [0, 2500, 2600, 4200, 3400, 2500, 4500, 1500, 1800, 1900, 2600, 3100, 3600]
workdays_per_month = [0, 21, 14, 20, 23, 18, 15, 20, 14, 20, 22, 20, 21]
initial_manufacturing_cost_per_case = 120
initial_extra_manufacturing_cost_per_case = 150
production_threshold = 3250
initial_holding_cost_per_case_per_month = 4.4
initial_workers = 21
initial_inventory = 600
final_inventory_target = 2300
hours_per_case = 0.2
hours_per_workday = 8
initial_hiring_cost_per_worker = 4000
initial_firing_cost_per_worker = 10000
inflation_rate = 0.04

# Initialize model
model = gp.Model("TomKon Workforce and Inventory Management")

# Number of months including initial and final points
num_months = 13

# Decision Variables
workers = model.addVars(num_months, name="workers", vtype=GRB.INTEGER, lb=0)
hiring = model.addVars(num_months, name="hiring", vtype=GRB.INTEGER, lb=0)
firing = model.addVars(num_months, name="firing", vtype=GRB.INTEGER, lb=0)
inventory = model.addVars(num_months, name="inventory", vtype=GRB.CONTINUOUS, lb=0)
production = model.addVars(num_months, name="production", vtype=GRB.CONTINUOUS, lb=0)
excess_production = model.addVars(num_months, name="excess_production", vtype=GRB.CONTINUOUS, lb=0)

# Calculate inflated costs for each month
manufacturing_cost = [initial_manufacturing_cost_per_case if t < 2 else initial_manufacturing_cost_per_case * (1 + inflation_rate) ** (t - 1) for t in range(num_months)]
extra_manufacturing_cost = [initial_extra_manufacturing_cost_per_case if t < 2 else initial_extra_manufacturing_cost_per_case * (1 + inflation_rate) ** (t - 1) for t in range(num_months)]
holding_cost = [initial_holding_cost_per_case_per_month if t < 2 else initial_holding_cost_per_case_per_month * (1 + inflation_rate) ** (t - 1) for t in range(num_months)]
hiring_cost = [initial_hiring_cost_per_worker if t < 2 else initial_hiring_cost_per_worker * (1 + inflation_rate) ** (t - 1) for t in range(num_months)]
firing_cost = [initial_firing_cost_per_worker if t < 2 else initial_firing_cost_per_worker * (1 + inflation_rate) ** (t - 1) for t in range(num_months)]

# Objective Function: Minimize total cost
total_manufacturing_cost = gp.quicksum(((1 + inflation_rate) ** (t - 1)) * (initial_manufacturing_cost_per_case * production[t] + initial_extra_manufacturing_cost_per_case * excess_production[t]) for t in range(1, num_months))
total_holding_cost = gp.quicksum(holding_cost[t] * inventory[t] for t in range(1, num_months))
total_hiring_cost = gp.quicksum(hiring_cost[t] * hiring[t] for t in range(1, num_months))
total_firing_cost = gp.quicksum(firing_cost[t] * firing[t] for t in range(1, num_months))
total_cost = total_manufacturing_cost + total_holding_cost + total_hiring_cost + total_firing_cost
model.setObjective(total_cost, GRB.MINIMIZE)

# Constraints
# Initial inventory
model.addConstr(inventory[0] == initial_inventory, "initial_inventory")

# Inventory balance constraints
for t in range(1, num_months):
    model.addConstr(inventory[t] == inventory[t - 1] + production[t] + excess_production[t] - monthly_demand[t], f"inventory_balance_{t}")

# Production capacity constraints
for t in range(1, num_months):
    model.addConstr(hours_per_case * (production[t] + excess_production[t]) <= workdays_per_month[t] * workers[t], f"production_capacity_{t}")
    model.addConstr(production[t] <= production_threshold, f"production_threshold_{t}")

# Workforce balance constraints
model.addConstr(workers[0] == initial_workers, "initial_workforce_balance")
for t in range(1, num_months):
    model.addConstr(workers[t] == workers[t - 1] + hiring[t] - firing[t], f"workforce_balance_{t}")

# Workforce change constraint (30%)
for t in range(1, num_months):
    model.addConstr(workers[t] <= 1.3 * workers[t - 1], f"workforce_increase_limit_{t}")
    model.addConstr(workers[t] >= 0.7 * workers[t - 1], f"workforce_decrease_limit_{t}")

# Excess production constraint
for t in range(1, num_months):
    model.addConstr(excess_production[t] >= production[t] - production_threshold, f"excess_production_{t}")
    model.addConstr(excess_production[t] >= 0, f"non_negative_excess_production_{t}")

# End-of-year inventory target
model.addConstr(inventory[num_months - 1] == final_inventory_target, "end_of_year_inventory")

# Solve model
model.optimize()




# Output results
if model.status == GRB.OPTIMAL:
    for t in range(num_months):
        print(f"Month {t}: Workers = {round(workers[t].X)}, Hiring = {round(hiring[t].X)}, Firing = {round(firing[t].X)}, Production = {round(production[t].X)}, Excess Production = {round(excess_production[t].X)}, Inventory = {round(inventory[t].X)}")
    total_manufacturing_cost = sum(((1 + inflation_rate) ** (t - 1)) * (initial_manufacturing_cost_per_case * production[t].X + initial_extra_manufacturing_cost_per_case * excess_production[t].X) for t in range(0, num_months))
    total_holding_cost = sum(holding_cost[t] * inventory[t].X for t in range(1, num_months))
    total_hiring_cost = sum(hiring_cost[t] * hiring[t].X for t in range(1, num_months))
    total_firing_cost = sum(firing_cost[t] * firing[t].X for t in range(1, num_months))
    total_cost = total_manufacturing_cost + total_holding_cost + total_hiring_cost + total_firing_cost
    print(f"Manufacturing cost: {total_manufacturing_cost:.2f} TL")
    print(f"Holding cost: {total_holding_cost:.2f} TL")
    print(f"Hiring cost: {total_hiring_cost:.2f} TL")
    print(f"Firing cost: {total_firing_cost:.2f} TL")
    print(f"Total cost: {round(total_cost)}")
else:
    print("No optimal solution found.")


# Explanation:
# Inflation Adjustment:
# 
# For each cost component (manufacturing, hiring, layoff, and storage), the cost is multiplied by (1.04)^m 
# to account for monthly inflation.
# 
# Objective Function:
# 
# The objective function has been modified to include the inflation-adjusted costs:
# base_manufacture_cost_per_case * (inflation_rate ** m) * regular_production[m]: Adjusted manufacturing cost for regular production.
# increased_manufacture_cost_per_case * (inflation_rate ** m) * excess_production[m]: Adjusted manufacturing cost for excess production.
# base_storage_cost_per_case * (inflation_rate ** m) * inventory[m]: Adjusted storage cost.
# base_hire_cost * (inflation_rate ** m) * hiring[m]: Adjusted hiring cost.
# base_layoff_cost * (inflation_rate ** m) * layoff[m]: Adjusted layoff cost.
# 
# This modified implementation ensures that the cost calculations reflect the effect of inflation over the 12-month period. 

# #Question 2

# #Part A

# In[12]:


import math

def EOQ_calculator(h, b, k, c, lammda, backorders_allowed=True):
    if backorders_allowed:
        omega = b / (h + b)
        Q_star = ((2 * k * lammda) / (h * omega)) ** 0.5
        r_star = -(1 - omega) * Q_star
    else:
        Q_star = ((2 * k * lammda) / h) ** 0.5
        r_star = 0
    
    return calculate_costs(h, b, k, lammda, c, Q_star, r_star, backorders_allowed=backorders_allowed)

def calculate_costs(h, b, k, lammda, c, Q, r, backorders_allowed=True):
    I_average = ((r + Q) ** 2) / (2 * Q)
    fixed_cost_per_unit_time = k / (Q / lammda)
    holding_cost_per_unit_time = h * I_average
    total_replenishment_cost_per_unit_time = fixed_cost_per_unit_time + (c * lammda)
    
    if backorders_allowed:
        B_average = (r ** 2) / (2 * Q)
        backorder_cost_per_unit_time = b * B_average
        return {
            "I_average": I_average,
            "B_average": B_average,
            "fixed_cost_per_unit_time": fixed_cost_per_unit_time,
            "holding_cost_per_unit_time": holding_cost_per_unit_time,
            "backorder_cost_per_unit_time": backorder_cost_per_unit_time,
            "total_replenishment_cost_per_unit_time": total_replenishment_cost_per_unit_time,
            "Q_star": Q,
            "r_star": r
        }
    else:
        return {
            "I_average": I_average,
            "fixed_cost_per_unit_time": fixed_cost_per_unit_time,
            "holding_cost_per_unit_time": holding_cost_per_unit_time,
            "total_replenishment_cost_per_unit_time": total_replenishment_cost_per_unit_time,
            "Q_star": Q
        }

# Parameters
holding_cost_rate = 0.22 / 12  # Monthly holding cost rate
h = 2.80 * holding_cost_rate  # Holding cost per unit per month
b = 2.80  # Backorder cost per unit per month (assumed same as unit cost for simplicity)
k = 20  # Fixed ordering cost per order
c = 2.80  # Cost per unit
lambda_ = 60  # Demand rate per month

# EOQ with backorders allowed
results_with_backorders = EOQ_calculator(h, b, k, c, lambda_, backorders_allowed=True)
print("With backorders allowed:")
for key, value in results_with_backorders.items():
    print(f"{key}: {value:.2f}")

# EOQ without backorders allowed
results_without_backorders = EOQ_calculator(h, b, k, c, lambda_, backorders_allowed=False)
print("\nWithout backorders allowed:")
for key, value in results_without_backorders.items():
    print(f"{key}: {value:.2f}")


# #Part B

# In[13]:


import math

def EOQ_calculator(h, k, lammda):
    Q_star = ((2 * k * lammda) / h) ** 0.5
    return Q_star

# Parameters
holding_cost_rate = 0.22 / 12  # Monthly holding cost rate
h = 2.80 * holding_cost_rate  # Holding cost per unit per month
k = 20  # Fixed ordering cost per order
lambda_ = 60  # Demand rate per month

# Calculate EOQ without backorders
Q_star = EOQ_calculator(h, k, lambda_)

# Calculate the order frequency (how often orders should be placed)
order_frequency_months = Q_star / lambda_

print(f"Optimal order quantity (Q*): {Q_star:.2f} boxes")
print(f"Order frequency: every {order_frequency_months:.2f} months")


# #Part C

# In[14]:


import math

def EOQ_calculator(h, k, lammda):
    Q_star = ((2 * k * lammda) / h) ** 0.5
    return Q_star

def calculate_annual_costs(Q_star, h, k, lammda):
    annual_holding_cost = (Q_star / 2) * h * 12
    annual_fixed_ordering_cost = (lammda / Q_star) * k * 12
    return annual_holding_cost, annual_fixed_ordering_cost

# Parameters
holding_cost_rate = 0.22 / 12  # Monthly holding cost rate
h = 2.80 * holding_cost_rate  # Holding cost per unit per month
k = 20  # Fixed ordering cost per order
lambda_ = 60  # Demand rate per month

# Calculate EOQ without backorders
Q_star = EOQ_calculator(h, k, lambda_)

# Calculate annual holding and fixed ordering costs
annual_holding_cost, annual_fixed_ordering_cost = calculate_annual_costs(Q_star, h, k, lambda_)

# Print results
print(f"Optimal order quantity (Q*): {Q_star:.2f} boxes")
print(f"Annual holding cost: {annual_holding_cost:.2f} TL")
print(f"Annual fixed ordering cost: {annual_fixed_ordering_cost:.2f} TL")


# #Part D

# In a small store like Peet's in Menlo Park, several factors can affect the implementation of the EOQ model calculated in part (a). Here are some considerations that might impact the recommended solution:
# 
# Space Constraints
# Storage Space Limitations:
# 
# Problem: A small store has limited storage space, which can restrict the maximum number of boxes they can store at any given time.
# Impact: The optimal order quantity 𝑄∗ calculated might be higher than what the store can physically accommodate. This means that while the EOQ model suggests a certain order quantity to minimize costs, the store might not have the capacity to store that many boxes.
# Solution: The store may need to adjust the order quantity to fit their storage constraints. This might involve ordering more frequently in smaller quantities, which could increase the fixed ordering costs but would be necessary to avoid space issues.
# Operational Constraints
# Inventory Management:
# 
# Problem: Managing larger inventories in a small space can lead to operational challenges, such as difficulty in organizing and accessing the inventory.
# Impact: This can lead to inefficiencies and potentially increased handling costs, which are not accounted for in the basic EOQ model.
# Solution: Implementing better inventory management practices, such as just-in-time (JIT) ordering, can help mitigate these issues by reducing the amount of inventory on hand at any given time.
# Cash Flow Constraints
# Capital Availability:
# 
# Problem: Small stores often have limited cash flow, which can affect their ability to purchase larger quantities of inventory at once.
# Impact: The optimal order quantity 𝑄∗ might require a significant upfront investment that the store cannot afford, even if it is cost-effective in the long run.
# Solution: The store might need to order in smaller quantities more frequently to align with their cash flow capabilities, even though this might increase the total cost.
# Demand Variability
# Demand Uncertainty:
# 
# Problem: Small stores may experience more significant fluctuations in demand due to their smaller customer base.
# Impact: The EOQ model assumes a steady demand rate (λ), but if demand varies significantly, the store might face stockouts or excess inventory.
# Solution: The store might need to adopt a more flexible inventory policy, such as a dynamic reorder point that adjusts based on recent sales data.
# Real-World Application
# Practical Considerations:
# 
# Problem: The EOQ model is a theoretical construct that may not account for all real-world variables specific to a small store.
# Impact: Factors such as supplier reliability, delivery schedules, and lead times can also affect inventory decisions.
# Solution: The store should consider these practical aspects when implementing the EOQ model and might need to adapt the theoretical solution to better fit their operational realities.
# Adjusted EOQ Model
# To account for these constraints, Peet's might consider an adjusted inventory policy that includes:
# 
# Smaller order quantities: Aligning orders with available storage space and cash flow.
# Frequent orders: Placing orders more frequently to ensure a steady supply without overwhelming storage capacity.
# Safety stock: Keeping a buffer stock to account for demand variability and lead time uncertainties.
# Conclusion
# While the EOQ model provides a useful starting point for determining optimal order quantities and reorder levels, small stores like Peet's need to consider their unique constraints and adapt the model accordingly. This might involve accepting higher ordering costs in exchange for operational feasibility and flexibility.
# 
# By balancing theoretical recommendations with practical considerations, Peet's can develop an inventory strategy that suits its specific needs and limitations.

# #Part E

# In[18]:


import math

def EOQ_calculator(h, k, lammda):
    Q_star = ((2 * k * lammda) / h) ** 0.5
    return Q_star

def calculate_costs(h, b, k, lammda, c, Q, r, backorders_allowed=True):
    I_average = Q / 2  # Average inventory level when no backorders are allowed
    fixed_cost_per_unit_time = (k * lammda) / Q
    holding_cost_per_unit_time = h * I_average
    total_replenishment_cost_per_unit_time = fixed_cost_per_unit_time + (c * lammda) + holding_cost_per_unit_time

    if backorders_allowed:
        B_average = (r ** 2) / (2 * Q)
        backorder_cost_per_unit_time = b * B_average
        return {
            "I_average": I_average,
            "B_average": B_average,
            "fixed_cost_per_unit_time": fixed_cost_per_unit_time,
            "holding_cost_per_unit_time": holding_cost_per_unit_time,
            "backorder_cost_per_unit_time": backorder_cost_per_unit_time,
            "total_replenishment_cost_per_unit_time": total_replenishment_cost_per_unit_time,
            "Q_star": Q,
            "r_star": r
        }
    else:
        return {
            "I_average": I_average,
            "fixed_cost_per_unit_time": fixed_cost_per_unit_time,
            "holding_cost_per_unit_time": holding_cost_per_unit_time,
            "total_replenishment_cost_per_unit_time": total_replenishment_cost_per_unit_time,
            "Q_star": Q
        }

# Parameters
holding_cost_rate = 0.22 / 12  # Monthly holding cost rate
h = 2.80 * holding_cost_rate  # Holding cost per unit per month
b = 2.80  # Backorder cost per unit per month (assumed same as unit cost for simplicity)
k = 20  # Fixed ordering cost per order
c = 2.80  # Cost per unit
lambda_ = 60  # Demand rate per month

# Calculate EOQ without backorders
Q_star = EOQ_calculator(h, k, lambda_)

# Calculate costs for different fractions of Q_star
fractions = [1, 0.8, 0.6, 0.4, 0.2]

print(f"Optimal order quantity (Q*): {Q_star:.2f} boxes")

for fraction in fractions:
    Q = fraction * Q_star
    costs = calculate_costs(h, b, k, lambda_, c, Q, 0, backorders_allowed=False)
    print(f"\nFor {fraction:.1f} * Q_star:")
    print(f"Order Quantity: {costs['Q_star']:.2f} boxes")
    print(f"Average Annual Holding Cost: {costs['holding_cost_per_unit_time'] * 12:.2f} TL")
    print(f"Average Annual Fixed Ordering Cost: {costs['fixed_cost_per_unit_time'] * 12:.2f} TL")
    print(f"Total Annual Cost: {costs['total_replenishment_cost_per_unit_time'] * 12:.2f} TL")

# Re-calculate and print the optimal costs
optimal_costs = calculate_costs(h, b, k, lambda_, c, Q_star, 0, backorders_allowed=False)
print(f"\nOptimal costs:")
print(f"  Annual Holding Cost: {optimal_costs['holding_cost_per_unit_time'] * 12:.2f} TL")
print(f"  Annual Fixed Ordering Cost: {optimal_costs['fixed_cost_per_unit_time'] * 12:.2f} TL")
print(f"  Total Annual Cost: {optimal_costs['total_replenishment_cost_per_unit_time'] * 12:.2f} TL")


# In[ ]:




