// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MITO",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .executable(name: "MITO", targets: ["MITO"])
    ],
    dependencies: [],
    targets: [
        .executableTarget(
            name: "MITO",
            dependencies: [],
            path: "Sources"
        )
    ]
)
