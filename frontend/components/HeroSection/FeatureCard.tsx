import { FeatureCardProps } from "./types"

export default function FeatureCard({
  icon: Icon,
  title,
  description,
  iconBgColor,
  iconColor
}: FeatureCardProps) {
  return (
    <div className="flex items-center space-x-3 p-4 bg-white/70 backdrop-blur-sm rounded-lg border border-gray-200">
      <div className={`w-10 h-10 ${iconBgColor} rounded-lg flex items-center justify-center`}>
        <Icon className={`w-5 h-5 ${iconColor}`} />
      </div>
      <div>
        <p className="font-medium text-gray-900">{title}</p>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
    </div>
  )
}