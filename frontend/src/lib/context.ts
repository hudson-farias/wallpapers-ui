import { getContext, setContext } from 'svelte';
import type { Screen } from '$lib/api';

export type AppContext = {
  screens: Screen[];
  dbusAvailable: boolean;
  getScreenId: () => number;
  setScreenId: (value: number) => void;
};

const APP_CONTEXT_KEY = Symbol('wallpaper-ui-app');

export function setAppContext(context: AppContext) {
  setContext(APP_CONTEXT_KEY, context);
}

export function getAppContext(): AppContext {
  return getContext<AppContext>(APP_CONTEXT_KEY);
}
