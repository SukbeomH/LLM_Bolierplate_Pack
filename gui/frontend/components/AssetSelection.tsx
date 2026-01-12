/**
 * AssetSelection 컴포넌트
 * 자산 선택 UI
 */

import { useState, useEffect } from "react";
import { ASSETS, type AssetType } from "@/lib/types";

interface AssetSelectionProps {
	onSelectionChange: (selectedAssets: string[]) => void;
}

export default function AssetSelection({ onSelectionChange }: AssetSelectionProps) {
	const [selected, setSelected] = useState<Set<AssetType>>(
		new Set(ASSETS.filter((a) => a.required).map((a) => a.id)),
	);

	useEffect(() => {
		onSelectionChange(Array.from(selected));
	}, [selected, onSelectionChange]);

	const handleToggle = (assetId: AssetType) => {
		const asset = ASSETS.find((a) => a.id === assetId);
		if (asset?.required) {
			return; // 필수 항목은 선택 해제 불가
		}

		setSelected((prev) => {
			const next = new Set(prev);
			if (next.has(assetId)) {
				next.delete(assetId);
			} else {
				next.add(assetId);
			}
			return next;
		});
	};

	const handleSelectAll = () => {
		setSelected(new Set(ASSETS.map((a) => a.id)));
	};

	const handleDeselectAll = () => {
		setSelected(new Set(ASSETS.filter((a) => a.required).map((a) => a.id)));
	};

	return (
		<div style={{ marginBottom: "2rem" }}>
			<div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
				<h2 style={{ fontSize: "1.5rem", fontWeight: "bold" }}>주입할 자산 선택</h2>
				<div style={{ display: "flex", gap: "0.5rem" }}>
					<button
						onClick={handleSelectAll}
						style={{
							padding: "0.25rem 0.5rem",
							border: "1px solid #ccc",
							borderRadius: "4px",
							cursor: "pointer",
							fontSize: "0.9rem",
						}}
					>
						전체 선택
					</button>
					<button
						onClick={handleDeselectAll}
						style={{
							padding: "0.25rem 0.5rem",
							border: "1px solid #ccc",
							borderRadius: "4px",
							cursor: "pointer",
							fontSize: "0.9rem",
						}}
					>
						필수만 선택
					</button>
				</div>
			</div>

			<div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
				{ASSETS.map((asset) => (
					<label
						key={asset.id}
						style={{
							display: "flex",
							alignItems: "flex-start",
							padding: "1rem",
							border: "1px solid #ddd",
							borderRadius: "4px",
							cursor: asset.required ? "default" : "pointer",
							backgroundColor: selected.has(asset.id) ? "#f0f8ff" : "white",
						}}
					>
						<input
							type="checkbox"
							checked={selected.has(asset.id)}
							onChange={() => handleToggle(asset.id)}
							disabled={asset.required}
							style={{ marginRight: "0.75rem", marginTop: "0.25rem" }}
						/>
						<div style={{ flex: 1 }}>
							<div style={{ fontWeight: "bold", marginBottom: "0.25rem" }}>
								{asset.label}
								{asset.required && (
									<span style={{ color: "#c33", fontSize: "0.9rem", marginLeft: "0.5rem" }}>(필수)</span>
								)}
							</div>
							<div style={{ fontSize: "0.9rem", color: "#666" }}>{asset.description}</div>
						</div>
					</label>
				))}
			</div>
		</div>
	);
}

