/**
 * StepIndicator 컴포넌트
 * 튜토리얼 단계를 시각적으로 표시합니다.
 */

interface StepIndicatorProps {
	currentStep: number;
	totalSteps: number;
	steps: Array<{ title: string; completed?: boolean }>;
	onStepClick?: (step: number) => void;
	completedSteps?: number[];
}

export default function StepIndicator({
	currentStep,
	totalSteps,
	steps,
	onStepClick,
	completedSteps = [],
}: StepIndicatorProps) {
	return (
		<div className="flex items-center justify-between mb-8">
			{steps.map((step, index) => {
				const stepNumber = index + 1;
				const isActive = stepNumber === currentStep;
				const isCompleted = step.completed || stepNumber < currentStep || completedSteps.includes(stepNumber);
				const isClickable = onStepClick !== undefined;

				return (
					<div key={index} className="flex items-center flex-1">
						{/* Step Circle */}
						<div className="flex flex-col items-center flex-1">
							<button
								type="button"
								onClick={() => isClickable && onStepClick?.(stepNumber)}
								disabled={!isClickable}
								className={`
									w-12 h-12 rounded-full flex items-center justify-center font-semibold
									transition-all duration-200
									${
										isCompleted
											? "bg-green-500 dark:bg-green-600 text-white"
											: isActive
											? "bg-blue-500 dark:bg-blue-600 text-white ring-4 ring-blue-200 dark:ring-blue-800"
											: "bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
									}
									${isClickable ? "cursor-pointer hover:scale-110" : "cursor-default"}
								`}
							>
								{isCompleted ? "✓" : stepNumber}
							</button>
							{/* Step Title */}
							<div
								className={`mt-2 text-xs text-center max-w-[100px] ${
									isActive
										? "font-semibold text-blue-600 dark:text-blue-400"
										: "text-gray-600 dark:text-gray-400"
								}`}
							>
								{step.title}
							</div>
						</div>
						{/* Connector Line */}
						{index < steps.length - 1 && (
							<div
								className={`flex-1 h-1 mx-2 ${
									isCompleted
										? "bg-green-500 dark:bg-green-600"
										: "bg-gray-200 dark:bg-gray-700"
								}`}
							/>
						)}
					</div>
				);
			})}
		</div>
	);
}

