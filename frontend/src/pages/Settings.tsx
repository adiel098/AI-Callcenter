import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { Settings as SettingsIcon, Save, RotateCcw, Loader2, Mic } from 'lucide-react';
import { motion } from 'framer-motion';
import { getSystemPrompt, updateSystemPrompt, getDefaultSystemPrompt, getAvailableVoices, getDefaultVoice, updateDefaultVoice } from '../services/api';

export default function Settings() {
  const queryClient = useQueryClient();
  const [promptValue, setPromptValue] = useState('');
  const [isDirty, setIsDirty] = useState(false);
  const [lastSaved, setLastSaved] = useState<string | null>(null);

  // Voice settings state
  const [selectedVoice, setSelectedVoice] = useState<{ id: string; name: string } | null>(null);
  const [voiceDirty, setVoiceDirty] = useState(false);

  // Fetch current system prompt
  const { data: currentPrompt, isLoading } = useQuery({
    queryKey: ['systemPrompt'],
    queryFn: getSystemPrompt,
  });

  // Fetch default prompt (for reset functionality)
  const { data: defaultPrompt } = useQuery({
    queryKey: ['defaultSystemPrompt'],
    queryFn: getDefaultSystemPrompt,
  });

  // Fetch available voices
  const { data: availableVoices, isLoading: voicesLoading } = useQuery({
    queryKey: ['availableVoices'],
    queryFn: getAvailableVoices,
  });

  // Fetch current default voice
  const { data: currentVoice } = useQuery({
    queryKey: ['defaultVoice'],
    queryFn: getDefaultVoice,
  });

  // Update prompt mutation
  const updateMutation = useMutation({
    mutationFn: updateSystemPrompt,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['systemPrompt'] });
      setIsDirty(false);
      setLastSaved(new Date().toLocaleString());
      toast.success('System prompt updated successfully', {
        description: 'Changes will apply to new calls immediately',
      });
    },
    onError: (error: any) => {
      toast.error('Failed to update system prompt', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });

  // Update voice mutation
  const updateVoiceMutation = useMutation({
    mutationFn: ({ voiceId, voiceName }: { voiceId: string; voiceName: string }) =>
      updateDefaultVoice(voiceId, voiceName),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['defaultVoice'] });
      setVoiceDirty(false);
      toast.success('Voice updated successfully', {
        description: 'Changes will apply to new calls immediately',
      });
    },
    onError: (error: any) => {
      toast.error('Failed to update voice', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });

  // Initialize prompt value when data loads
  useEffect(() => {
    if (currentPrompt?.value) {
      setPromptValue(currentPrompt.value);
      if (currentPrompt.updated_at !== 'N/A') {
        setLastSaved(new Date(currentPrompt.updated_at).toLocaleString());
      }
    }
  }, [currentPrompt]);

  // Initialize voice selection when data loads
  useEffect(() => {
    if (currentVoice?.voice_id && currentVoice?.voice_name) {
      setSelectedVoice({ id: currentVoice.voice_id, name: currentVoice.voice_name });
    }
  }, [currentVoice]);

  const handleSave = () => {
    if (!promptValue.trim()) {
      toast.error('System prompt cannot be empty');
      return;
    }

    updateMutation.mutate(promptValue);
  };

  const handleReset = () => {
    if (defaultPrompt?.default_prompt) {
      setPromptValue(defaultPrompt.default_prompt);
      setIsDirty(true);
      toast.info('Prompt reset to default', {
        description: 'Click "Save Changes" to apply',
      });
    }
  };

  const handleChange = (value: string) => {
    setPromptValue(value);
    setIsDirty(value !== currentPrompt?.value);
  };

  const handleVoiceChange = (voiceId: string) => {
    const voice = availableVoices?.find((v: any) => v.voice_id === voiceId);
    if (voice) {
      setSelectedVoice({ id: voice.voice_id, name: voice.name });
      setVoiceDirty(voice.voice_id !== currentVoice?.voice_id);
    }
  };

  const handleSaveVoice = () => {
    if (selectedVoice) {
      updateVoiceMutation.mutate({ voiceId: selectedVoice.id, voiceName: selectedVoice.name });
    }
  };

  const characterCount = promptValue.length;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <SettingsIcon className="w-6 h-6 text-blue-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Settings
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Configure your AI call agent
              </p>
            </div>
          </div>

          {lastSaved && (
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Last saved: {lastSaved}
            </div>
          )}
        </div>

        {/* System Prompt Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  System Prompt
                </h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  This prompt defines how your AI agent behaves during calls. You can add meeting context, product information, or specific instructions.
                </p>
              </div>
            </div>

            {/* Textarea */}
            <div className="space-y-4">
              {isLoading ? (
                <div className="flex items-center justify-center py-20">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                </div>
              ) : (
                <>
                  <textarea
                    value={promptValue}
                    onChange={(e) => handleChange(e.target.value)}
                    className="w-full h-96 px-4 py-3 font-mono text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-900 dark:text-gray-100 resize-none"
                    placeholder="Enter your system prompt here..."
                    spellCheck={false}
                  />

                  {/* Character count */}
                  <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                    <span>{characterCount.toLocaleString()} characters</span>
                    {isDirty && (
                      <span className="text-amber-500 dark:text-amber-400">
                        Unsaved changes
                      </span>
                    )}
                  </div>

                  {/* Help text */}
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-2">
                      Tips for a great prompt:
                    </h3>
                    <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1 list-disc list-inside">
                      <li>Include specific meeting topics and agenda items</li>
                      <li>Add product/service details the AI should mention</li>
                      <li>Specify tone and conversation style</li>
                      <li>Include handling instructions for common objections</li>
                      <li>Keep responses concise for natural phone conversation</li>
                    </ul>
                  </div>

                  {/* Action buttons */}
                  <div className="flex items-center gap-3 pt-4">
                    <button
                      onClick={handleSave}
                      disabled={!isDirty || updateMutation.isPending}
                      className="flex items-center gap-2 px-6 py-2.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                    >
                      {updateMutation.isPending ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Saving...
                        </>
                      ) : (
                        <>
                          <Save className="w-4 h-4" />
                          Save Changes
                        </>
                      )}
                    </button>

                    <button
                      onClick={handleReset}
                      disabled={updateMutation.isPending}
                      className="flex items-center gap-2 px-6 py-2.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                    >
                      <RotateCcw className="w-4 h-4" />
                      Reset to Default
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Voice Settings Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mt-6">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-purple-500/10 rounded-lg">
                <Mic className="w-5 h-5 text-purple-500" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Voice Settings
                </h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Select the default voice for all outbound calls
                </p>
              </div>
            </div>

            {voicesLoading ? (
              <div className="flex items-center justify-center py-10">
                <Loader2 className="w-6 h-6 animate-spin text-purple-500" />
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Default Voice
                  </label>
                  <select
                    value={selectedVoice?.id || ''}
                    onChange={(e) => handleVoiceChange(e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-900 dark:text-gray-100"
                  >
                    <option value="">Use language-based default</option>
                    {availableVoices?.map((voice: any) => (
                      <option key={voice.voice_id} value={voice.voice_id}>
                        {voice.name}
                      </option>
                    ))}
                  </select>
                  {voiceDirty && (
                    <p className="mt-2 text-sm text-amber-500 dark:text-amber-400">
                      Unsaved changes
                    </p>
                  )}
                </div>

                <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-purple-900 dark:text-purple-100 mb-2">
                    About Voice Selection
                  </h3>
                  <p className="text-sm text-purple-800 dark:text-purple-200">
                    If no default voice is set, the system will automatically select a voice based on the lead's country code. You can override this by selecting a specific voice here.
                  </p>
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <button
                    onClick={handleSaveVoice}
                    disabled={!voiceDirty || updateVoiceMutation.isPending}
                    className="flex items-center gap-2 px-6 py-2.5 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                  >
                    {updateVoiceMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4" />
                        Save Voice
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Info cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-green-900 dark:text-green-100 mb-2">
              Immediate Effect
            </h3>
            <p className="text-sm text-green-800 dark:text-green-200">
              Changes apply instantly to all new calls. No need to restart workers or services.
            </p>
          </div>

          <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-purple-900 dark:text-purple-100 mb-2">
              AI Tools Available
            </h3>
            <p className="text-sm text-purple-800 dark:text-purple-200">
              The AI can check calendar availability and book meetings automatically during calls.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
