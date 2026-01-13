/**
 * StepIndicator 컴포넌트
 * 튜토리얼 단계를 시각적으로 표시합니다.
 */

interface StepIndicatorProps {
	currentStep: number;
	totalSteps: number;
	steps: Array<{ title: string; completed?: boolean }>;
	onStepClick?: (step: number) => void;
}

export default function StepIndicator({
	currentStep,
	totalSteps,
	steps,
	onStepClick,
}: StepIndicatorProps) {
	return (
		<div className="flex items-center justify-between mb-8">
			{steps.map((step, index) => {
				const stepNumber = index + 1;
				const isActive = stepNumber === currentStep;
				const isCompleted = step.completed || stepNumber < currentStep;
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
											? "bg-green-500 text-white"
											: isActive
											? "bg-blue-500 text-white ring-4 ring-blue-200"
											: "bg-gray-200 text-gray-600"
									}
									${isClickable ? "cursor-pointer hover:scale-110" : "cursor-default"}
								`}
							>
								{isCompleted ? "✓" : stepNumber}
							</button>
							{/* Step Title */}
							<div
								className={`mt-2 text-xs text-center max-w-[100px] ${
									isActive ? "font-semibold text-blue-600" : "text-gray-600"
								}`}
							>
								{step.title}
							</div>
						</div>
						{/* Connector Line */}
						{index < steps.length - 1 && (
							<div
								className={`flex-1 h-1 mx-2 ${
									isCompleted ? "bg-green-500" : "bg-gray-200"
								}`}
							/>
						)}
					</div>
				);
			})}
		</div>
	);
}

