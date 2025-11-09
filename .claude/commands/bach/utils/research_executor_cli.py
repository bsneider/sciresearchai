#!/usr/bin/env python3
"""
Research CLI Wrapper for Bach Research Executor System

Provides command-line interface for research-focused bach commands to properly
navigate and update research execution state without manual JSON manipulation.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

from dependency_analyzer import find_project_root
from json_updater import JsonUpdater


class ResearchExecutorCLI:
    def __init__(self, tasks_dir: Optional[str] = None):
        if tasks_dir is None:
            try:
                project_root = find_project_root()
                tasks_dir = os.path.join(project_root, ".tasks")
            except ValueError as e:
                print(f"❌ {e}")
                sys.exit(1)
        self.tasks_dir = tasks_dir
        
        # Verify tasks directory exists
        if not os.path.exists(self.tasks_dir):
            print(f"❌ Bach research tasks directory not found: {self.tasks_dir}")
            print("   Make sure you're in a Bach research project with initialized .tasks directory")
            sys.exit(1)
            
        self._load_data()

    def _load_data(self):
        """Load all Bach Research JSON files"""
        self.task_graph = self._load_json("task_graph.json")
        self.research_progress_tracker = self._load_json("research_progress_tracker.json")
        self.research_guardrail_config = self._load_json("research_guardrail_config.json")
        self.research_strategy = self._load_json("research_strategy.json")

    def _load_json(self, filename: str) -> Dict:
        """Load JSON file from tasks directory"""
        try:
            path = os.path.join(self.tasks_dir, filename)
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Required file not found: {filename}")
            print(f"   Expected path: {path}")
            print("   Run `/bach:planner` first to initialize research workflow")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {filename}: {e}")
            sys.exit(1)

    def _save_data(self):
        """Save all modified data atomically"""
        updater = JsonUpdater(self.tasks_dir)
        
        # Update progress tracker
        updater.update_file("research_progress_tracker.json", self.research_progress_tracker)
        
        print("✅ Research state updated atomically")

    def get_current_status(self) -> Dict:
        """Get current research status and validation requirements"""
        tracker = self.research_progress_tracker
        
        # Check if validation is required
        validation_required = False
        blocked_reason = None
        
        # Check if current phase needs validation
        current_phase = tracker.get("current_phase", {})
        if current_phase.get("validation_required", False):
            validation_required = True
            blocked_reason = f"Phase {current_phase.get('id')} requires validation"
        
        return {
            "research_status": tracker.get("status", "unknown"),
            "current_phase": current_phase,
            "completed_tasks": tracker.get("tasks_completed", 0),
            "total_tasks": tracker.get("total_tasks", 0),
            "validation_required": validation_required,
            "blocked_reason": blocked_reason,
            "last_update": tracker.get("last_update", "unknown")
        }

    def get_next_task(self, task_id: Optional[str] = None) -> Dict:
        """Find next eligible research task or get specific task"""
        tasks = self.task_graph.get("tasks", [])
        
        if task_id:
            # Find specific task
            task = next((t for t in tasks if t["id"] == task_id), None)
            if not task:
                return {"error": f"Task {task_id} not found"}
            if task.get("status") == "completed":
                return {"error": f"Task {task_id} already completed"}
            return {"task": task}
        
        # Find next eligible task
        for task in tasks:
            if task.get("status") in ["not_started", "ready"]:
                # Check dependencies
                if self._check_dependencies(task):
                    return {"task": task}
        
        return {"error": "No eligible research tasks found"}

    def get_task_details(self, task_id: str) -> Dict:
        """Get comprehensive task details including research context"""
        tasks = self.task_graph.get("tasks", [])
        task = next((t for t in tasks if t["id"] == task_id), None)
        
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        # Get phase information
        phases = self.task_graph.get("phases", [])
        phase = next((p for p in phases if task.get("phase_id") == p["id"]), {})
        
        # Get research compliance
        research_compliance = self._check_research_compliance(task)
        
        # Get dependencies status
        dependencies = self._get_dependencies_status(task)
        
        return {
            "task": task,
            "phase": phase,
            "research_compliance": research_compliance,
            "dependencies": dependencies,
            "research_context": self._get_research_context(task)
        }

    def _check_research_compliance(self, task: Dict) -> Dict:
        """Check if task complies with approved research strategy"""
        database_context = task.get("database_context", {})
        approved_databases = self.research_strategy.get("databases", {})
        
        task_databases = [db["name"] for db in database_context.get("primary_databases", [])]
        approved_db_names = list(approved_databases.keys())
        
        non_compliant = [db for db in task_databases if db not in approved_db_names]
        
        return {
            "compliant": len(non_compliant) == 0,
            "non_compliant_databases": non_compliant,
            "approved_databases": approved_db_names
        }

    def _check_dependencies(self, task: Dict) -> bool:
        """Check if task dependencies are satisfied"""
        dependencies = task.get("dependencies", [])
        if not dependencies:
            return True
        
        completed_tasks = self.research_progress_tracker.get("completed_task_ids", [])
        return all(dep in completed_tasks for dep in dependencies)

    def _get_dependencies_status(self, task: Dict) -> Dict:
        """Get detailed dependency status"""
        dependencies = task.get("dependencies", [])
        completed_tasks = self.research_progress_tracker.get("completed_task_ids", [])
        
        satisfied = [dep for dep in dependencies if dep in completed_tasks]
        missing = [dep for dep in dependencies if dep not in completed_tasks]
        
        return {
            "total_dependencies": len(dependencies),
            "satisfied": len(missing) == 0,
            "satisfied_dependencies": satisfied,
            "missing": missing
        }

    def _get_research_context(self, task: Dict) -> Dict:
        """Get research-specific context for task"""
        return {
            "research_boundaries": task.get("research_boundaries", {}),
            "database_context": task.get("database_context", {}),
            "research_guards": task.get("research_guards", {}),
            "max_papers": task.get("scope_drift_prevention", {}).get("max_papers_per_task", 50)
        }

    def validate_dependencies(self, task_id: str) -> Dict:
        """Validate task dependencies are satisfied"""
        task_details = self.get_task_details(task_id)
        if "error" in task_details:
            return task_details
        
        return task_details["dependencies"]

    def check_scope_compliance(self, task_id: str) -> Dict:
        """Check research scope compliance for task"""
        task_details = self.get_task_details(task_id)
        if "error" in task_details:
            return task_details
        
        research_context = task_details["research_context"]
        research_boundaries = research_context["research_boundaries"]
        
        return {
            "must_research": research_boundaries.get("must_research", []),
            "must_not_research": research_boundaries.get("must_not_research", []),
            "max_papers": research_context["max_papers"],
            "scope_check": research_boundaries.get("scope_check", "BLOCK if not in must_research")
        }

    def start_task(self, task_id: str) -> Dict:
        """Mark research task as in-progress"""
        tasks = self.task_graph.get("tasks", [])
        task = next((t for t in tasks if t["id"] == task_id), None)
        
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        if task.get("status") == "completed":
            return {"error": f"Task {task_id} already completed"}
        
        if task.get("status") == "in_progress":
            return {"error": f"Task {task_id} already in progress"}
        
        # Check dependencies
        if not self._check_dependencies(task):
            deps_status = self._get_dependencies_status(task)
            return {"error": f"Dependencies not satisfied: {deps_status['missing']}"}
        
        # Update task status
        task["status"] = "in_progress"
        task["started_at"] = datetime.now().isoformat()
        
        # Update progress tracker
        self.research_progress_tracker["current_task_id"] = task_id
        self.research_progress_tracker["last_update"] = datetime.now().isoformat()
        
        self._save_data()
        
        return {"success": True, "task_id": task_id}

    def complete_task(self, task_id: str) -> Dict:
        """Mark research task as completed"""
        tasks = self.task_graph.get("tasks", [])
        task = next((t for t in tasks if t["id"] == task_id), None)
        
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        if task.get("status") != "in_progress":
            return {"error": f"Task {task_id} not in progress"}
        
        # Update task status
        task["status"] = "completed"
        task["completed_at"] = datetime.now().isoformat()
        
        # Update progress tracker
        completed_tasks = self.research_progress_tracker.get("completed_task_ids", [])
        if task_id not in completed_tasks:
            completed_tasks.append(task_id)
        
        self.research_progress_tracker["completed_task_ids"] = completed_tasks
        self.research_progress_tracker["tasks_completed"] = len(completed_tasks)
        self.research_progress_tracker["last_update"] = datetime.now().isoformat()
        
        # Check if phase is complete
        phase_complete, phase_info = self._check_phase_completion(task)
        
        result = {"success": True, "task_id": task_id}
        
        if phase_complete:
            result["phase_complete"] = True
            result["phase_id"] = phase_info["id"]
            result["phase_name"] = phase_info["name"]
            
            # Mark phase as needing validation
            self.research_progress_tracker["current_phase"]["validation_required"] = True
        
        self._save_data()
        
        return result

    def _check_phase_completion(self, completed_task: Dict) -> tuple[bool, Dict]:
        """Check if completing this task completes a research phase"""
        phase_id = completed_task.get("phase_id")
        if not phase_id:
            return False, {}
        
        phases = self.task_graph.get("phases", [])
        phase = next((p for p in phases if p["id"] == phase_id), {})
        
        if not phase:
            return False, {}
        
        # Get all tasks in this phase
        phase_tasks = [t for t in self.task_graph.get("tasks", []) if t.get("phase_id") == phase_id]
        completed_task_ids = self.research_progress_tracker.get("completed_task_ids", [])
        
        # Check if all phase tasks are completed
        all_completed = all(t["id"] in completed_task_ids for t in phase_tasks)
        
        return all_completed, phase

    def get_phase_status(self, phase_id: str) -> Dict:
        """Get detailed research phase status"""
        phases = self.task_graph.get("phases", [])
        phase = next((p for p in phases if p["id"] == phase_id), None)
        
        if not phase:
            return {"error": f"Phase {phase_id} not found"}
        
        # Get phase tasks
        phase_tasks = [t for t in self.task_graph.get("tasks", []) if t.get("phase_id") == phase_id]
        completed_task_ids = self.research_progress_tracker.get("completed_task_ids", [])
        
        completed_tasks = [t["id"] for t in phase_tasks if t["id"] in completed_task_ids]
        pending_tasks = [t["id"] for t in phase_tasks if t["id"] not in completed_task_ids]
        
        completion_percentage = (len(completed_tasks) / len(phase_tasks)) * 100 if phase_tasks else 0
        
        return {
            "phase_id": phase_id,
            "phase_name": phase.get("name", "Unknown"),
            "total_tasks": len(phase_tasks),
            "completed_tasks": len(completed_tasks),
            "pending_tasks": len(pending_tasks),
            "completion_percentage": round(completion_percentage, 1),
            "completed_task_ids": completed_tasks,
            "pending_task_ids": pending_tasks
        }


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Bach Research Executor CLI")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--tasks-dir", help="Path to .tasks directory")
    
    args = parser.parse_args()
    
    try:
        cli = ResearchExecutorCLI(args.tasks_dir)
        
        # Route commands
        if args.command == "get-current-status":
            result = cli.get_current_status()
        elif args.command == "get-next-task":
            task_id = args.args[0] if args.args else None
            result = cli.get_next_task(task_id)
        elif args.command == "get-task-details":
            if not args.args:
                print("❌ Task ID required")
                sys.exit(1)
            result = cli.get_task_details(args.args[0])
        elif args.command == "validate-dependencies":
            if not args.args:
                print("❌ Task ID required")
                sys.exit(1)
            result = cli.validate_dependencies(args.args[0])
        elif args.command == "check-scope-compliance":
            if not args.args:
                print("❌ Task ID required")
                sys.exit(1)
            result = cli.check_scope_compliance(args.args[0])
        elif args.command == "start-task":
            if not args.args:
                print("❌ Task ID required")
                sys.exit(1)
            result = cli.start_task(args.args[0])
        elif args.command == "complete-task":
            if not args.args:
                print("❌ Task ID required")
                sys.exit(1)
            result = cli.complete_task(args.args[0])
        elif args.command == "get-phase-status":
            if not args.args:
                print("❌ Phase ID required")
                sys.exit(1)
            result = cli.get_phase_status(args.args[0])
        else:
            print(f"❌ Unknown command: {args.command}")
            sys.exit(1)
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()