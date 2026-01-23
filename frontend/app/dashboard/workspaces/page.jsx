"use client";

import { useEffect, useState } from "react";
import { useWorkspaceStore } from "../../../stores/workspaceStore";
import { toast } from "sonner";
import Button from "../../../components/ui/Button";
import { Plus, Eye, Edit, Trash2 } from "lucide-react";

// Skeleton component for loading
const WorkspaceSkeleton = () => (
  <div className="bg-card border border-border rounded-lg p-6 animate-pulse">
    <div className="h-6 bg-muted rounded mb-2"></div>
    <div className="h-4 bg-muted rounded mb-1"></div>
    <div className="h-4 bg-muted rounded mb-4"></div>
    <div className="flex gap-2">
      <div className="h-8 w-16 bg-muted rounded"></div>
      <div className="h-8 w-16 bg-muted rounded"></div>
      <div className="h-8 w-16 bg-muted rounded"></div>
    </div>
  </div>
);

// Modal component for Add/Edit
const WorkspaceModal = ({ isOpen, onClose, workspace, onSave }) => {
  const [name, setName] = useState(workspace?.name || "");
  const [description, setDescription] = useState(workspace?.description || "");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({ name, description });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-card border border-border rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4">
          {workspace ? "Edit Workspace" : "Add Workspace"}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-md bg-background"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-md bg-background"
              rows={3}
            />
          </div>
          <div className="flex gap-2 justify-end">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">
              {workspace ? "Update" : "Create"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default function WorkspacesPage() {
  const {
    workspaces,
    listLoading,
    error,
    fetchWorkspaces,
    fetchWorkspaceById,
    createWorkspace,
    updateWorkspace,
    deleteWorkspace,
    clearWorkspaceError,
  } = useWorkspaceStore();

  const [showAddModal, setShowAddModal] = useState(false);
  const [editingWorkspace, setEditingWorkspace] = useState(null);

  // Fetch workspaces on mount
  useEffect(() => {
    fetchWorkspaces().catch(() => {
      // Error handled in store
    });
  }, [fetchWorkspaces]);

  // Handle errors with toast
  useEffect(() => {
    if (error) {
      toast.error(error);
      clearWorkspaceError();
    }
  }, [error, clearWorkspaceError]);

  // Handle add workspace
  const handleAddWorkspace = async (payload) => {
    try {
      await createWorkspace(payload);
      toast.success("Workspace created successfully");
      setShowAddModal(false);
    } catch (error) {
      toast.error("Failed to create workspace");
    }
  };

  // Handle edit workspace
  const handleEditWorkspace = async (payload) => {
    if (!editingWorkspace) return;
    try {
      await updateWorkspace(editingWorkspace.id, payload);
      toast.success("Workspace updated successfully");
      setEditingWorkspace(null);
    } catch (error) {
      toast.error("Failed to update workspace");
    }
  };

  // Handle delete workspace
  const handleDeleteWorkspace = async (workspaceId) => {
    if (!window.confirm("Are you sure you want to delete this workspace?")) return;
    try {
      await deleteWorkspace(workspaceId);
      toast.success("Workspace deleted successfully");
    } catch (error) {
      toast.error("Failed to delete workspace");
    }
  };

  // Handle view workspace (fetch details)
  const handleViewWorkspace = async (workspaceId) => {
    try {
      const workspace = await fetchWorkspaceById(workspaceId);
      // For now, just show a toast with details
      toast.success(`Viewing workspace: ${workspace.name}`);
      // In a real app, you might navigate or show details
    } catch (error) {
      toast.error("Failed to fetch workspace details");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-foreground">Workspaces</h1>
        <Button onClick={() => setShowAddModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Workspace
        </Button>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
          <p className="text-destructive">{error}</p>
        </div>
      )}

      {/* Workspaces Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {listLoading ? (
          // Show skeletons while loading
          Array.from({ length: 6 }).map((_, i) => <WorkspaceSkeleton key={i} />)
        ) : (
          workspaces.map((workspace) => (
            <div
              key={workspace.id}
              className="bg-card border border-border rounded-lg p-6 hover:shadow-lg transition-shadow duration-200"
            >
              <h3 className="text-lg font-semibold text-card-foreground mb-2">
                {workspace.name}
              </h3>
              <p className="text-sm text-muted-foreground mb-1">
                Owner: {workspace.owner || "Unknown"}
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                Last Updated: {new Date(workspace.updated_at).toLocaleDateString()}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleViewWorkspace(workspace.id)}
                >
                  <Eye className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setEditingWorkspace(workspace)}
                >
                  <Edit className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDeleteWorkspace(workspace.id)}
                  className="hover:bg-destructive hover:text-destructive-foreground"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modals */}
      <WorkspaceModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSave={handleAddWorkspace}
      />
      <WorkspaceModal
        isOpen={!!editingWorkspace}
        onClose={() => setEditingWorkspace(null)}
        workspace={editingWorkspace}
        onSave={handleEditWorkspace}
      />
    </div>
  );
}
