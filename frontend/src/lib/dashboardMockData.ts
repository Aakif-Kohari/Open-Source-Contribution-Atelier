interface CurrentModule {
  number: number;
  title: string;
  lessonsCompleted: number;
  totalLessons: number;
}

interface StudentStats {
  xp: number;
  streakDays: number;
  longestStreak: number;
  modulesCompleted: number;
  totalModules: number;
  totalLessonsCompleted: number;
  totalLessons: number;
  currentModule: CurrentModule;
  earnedBadges: string[];
}

interface LessonItem {
  number: number;
  title: string;
  description: string;
  slug: string;
}

interface TipOfTheDay {
  title: string;
  explanation: string;
}

const tips: TipOfTheDay[] = [
  {
    title: "What does git add do?",
    explanation:
      "Think of git add like packing a suitcase. You put your changed files (clothes) into the staging area (suitcase) before you commit (zip it up and label it). Until you git add, Git won't track your changes — they're just lying around your room!",
  },
  {
    title: "What is a commit?",
    explanation:
      "A commit is like saving a checkpoint in a video game. After you make changes and git add them, you commit to save that moment forever. If something breaks later, you can always go back to this checkpoint.",
  },
  {
    title: "What is a branch?",
    explanation:
      "A branch is like a separate timeline in a story. The main timeline (main branch) is the official story. When you want to try something new, you create a new branch — it's like writing an alternate version without messing up the original.",
  },
  {
    title: "What is a pull request?",
    explanation:
      "A pull request is like raising your hand to suggest a change. You've written some code on your branch, and now you're asking the project owner: 'Hey, I made this cool improvement — do you want to add it to the main story?'",
  },
  {
    title: "What is an open source license?",
    explanation:
      "A license is like a permission slip from the creator. It tells everyone: 'Yes, you can use my code, share it, and even improve it — as long as you follow these rules.' Without a license, it's legally unclear if anyone can use it.",
  },
  {
    title: "What does 'fork' mean?",
    explanation:
      "Forking is like making a photocopy of someone's recipe book. You now have your own copy that you can scribble in, try new recipes, and cook whatever you want. If you make something delicious, you can share it back with the original cook!",
  },
];

export function getTipOfTheDay(): TipOfTheDay {
  const dayIndex = new Date().getDate() % tips.length;
  return tips[dayIndex];
}

export const mockStudentStats: StudentStats = {
  xp: 2840,
  streakDays: 14,
  longestStreak: 21,
  modulesCompleted: 1,
  totalModules: 8,
  totalLessonsCompleted: 3,
  totalLessons: 48,
  currentModule: {
    number: 2,
    title: "Git Basics — Version Control for Beginners",
    lessonsCompleted: 3,
    totalLessons: 6,
  },
  earnedBadges: ["first-commit", "streak-7", "streak-14", "module-1"],
};

export const mockLessonQueue: LessonItem[] = [
  {
    number: 4,
    title: "What is a commit?",
    description:
      "Learn how to save your work with meaningful checkpoints",
    slug: "what-is-a-commit",
  },
  {
    number: 5,
    title: "Your first git add + commit",
    description:
      "Practice staging and committing changes like a pro",
    slug: "first-commit",
  },
  {
    number: 6,
    title: "Reading git status",
    description: "Understand what Git tells you about your files",
    slug: "git-status",
  },
];
